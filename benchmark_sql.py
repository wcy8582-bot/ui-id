# -*- coding: utf-8 -*-
"""
benchmark_sql.py —— 慢查询优化前后对比基准
==========================================
造一个临时 SQLite 库，灌入接近真实规模的数据
（1000 次执行 × 20 条用例，每条日志约 8KB），
对比三组优化前后的查询耗时：

  A. 列过滤：SELECT *（带 log 大字段） vs 显式列裁剪
  B. N+1：逐条查用例信息 vs 一次 IN 批量查询
  C. 超时检查：查出 running 再逐行 UPDATE vs 单条 UPDATE

运行: python benchmark_sql.py
"""
import os
import random
import sys
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.common.database import SQLiteDatabaseBackend

BENCH_DB = os.path.join("data", "benchmark_test.db")
N_EXECUTIONS = 500           # 执行记录数
CASES_PER_EXEC = 40          # 每次执行的用例数
N_RUNNING = 300              # running 状态的执行数（超时检查场景）
LOG_SIZE = 40000             # 单条日志字节数（贴近真实自动化日志量级）
REPEAT = 100                 # 每组查询重复次数取平均


def seed(db: SQLiteDatabaseBackend):
    """灌入测试数据"""
    conn = db.connection
    cur = conn.cursor()

    # 用例信息表
    cur.executemany(
        "INSERT INTO test_case_info (case_name, case_scene, project, module) VALUES (?,?,?,?)",
        [(f"case_{i:04d}", f"场景{i}", "LX", f"module_{i % 10}") for i in range(500)])

    log_body = "[INFO] step output line\n" * (LOG_SIZE // 24)
    base = datetime.now() - timedelta(days=90)

    exec_rows, case_rows = [], []
    for eid in range(1, N_EXECUTIONS + 1):
        start = base + timedelta(minutes=eid * 120)
        # 前 N_RUNNING 条设为 running 且启动时间在 3 小时前（必超时）
        if eid <= N_RUNNING:
            start = datetime.now() - timedelta(hours=3)
            status = "running"
        else:
            status = "completed"
        exec_rows.append((start.strftime('%Y-%m-%d %H:%M:%S'), status,
                          f"python run.py -p LX", "LX", 30))
        for c in range(CASES_PER_EXEC):
            case_rows.append((
                eid, f"case_{(eid * CASES_PER_EXEC + c) % 500:04d}",
                random.choice(["passed", "passed", "passed", "failed"]),
                round(random.uniform(1, 30), 2), log_body, None, "LX"))

    cur.executemany(
        "INSERT INTO test_execution (start_time, status, command, project, timeout_minutes)"
        " VALUES (?,?,?,?,?)", exec_rows)
    cur.executemany(
        "INSERT INTO test_case_result (execution_id, case_name, status, duration, log, error_message, project)"
        " VALUES (?,?,?,?,?,?,?)", case_rows)
    conn.commit()
    print(f"数据灌入完成: {N_EXECUTIONS} 次执行, "
          f"{N_EXECUTIONS * CASES_PER_EXEC} 条用例结果, "
          f"单条日志 ~{LOG_SIZE // 1024}KB")


def bench(label, fn, repeat=REPEAT):
    fn()  # 预热
    t0 = time.perf_counter()
    for _ in range(repeat):
        fn()
    ms = (time.perf_counter() - t0) / repeat * 1000
    print(f"  {label:<48} {ms:>8.2f} ms")
    return ms


def main():
    os.makedirs("data", exist_ok=True)
    if os.path.exists(BENCH_DB):
        os.remove(BENCH_DB)

    db = SQLiteDatabaseBackend(BENCH_DB)
    db.connect()
    db.create_tables()
    seed(db)

    exec_ids = [random.randint(N_RUNNING + 1, N_EXECUTIONS) for _ in range(REPEAT)]
    sample_names = [f"case_{i:04d}" for i in range(CASES_PER_EXEC)]

    print("\n=== A. 列过滤：报告页查一次执行的全部用例 ===")
    old_a = bench("旧: SELECT *（含 log 大字段）",
                  lambda: db.get_case_results_by_execution(exec_ids[0]))
    new_a = bench("新: 显式列裁剪（不含 log）",
                  lambda: db.get_case_results_summary(exec_ids[0]))

    print("\n=== B. N+1：报告页补充 20 条用例的场景信息 ===")
    old_b = bench("旧: 逐条 get_case_info_by_name（20 次查询）",
                  lambda: [db.get_case_info_by_name(n) for n in sample_names])
    new_b = bench("新: get_case_info_map（1 次 IN 查询）",
                  lambda: db.get_case_info_map(sample_names))

    print("\n=== C. 超时检查：每次访问执行记录页都触发 ===")

    def old_timeout_check():
        """旧逻辑：查出全部 running，再逐行 UPDATE"""
        cur = db.connection.cursor()
        cur.execute("SELECT id, start_time, timeout_minutes FROM test_execution WHERE status='running'")
        for r in cur.fetchall():
            db.update_execution_timeout(r["id"])

    # 旧逻辑会改动数据，每次测完要把 running 状态重置回去
    def old_c_once():
        old_timeout_check()
        cur = db.connection.cursor()
        cur.execute("UPDATE test_execution SET status='running', end_time=NULL "
                    "WHERE status='timeout'")
        db.connection.commit()
    def new_c_once():
        db.check_and_update_timeout_executions()
        cur = db.connection.cursor()
        cur.execute("UPDATE test_execution SET status='running', end_time=NULL "
                    "WHERE status='timeout'")
        db.connection.commit()

    old_c = bench("旧: SELECT running + 逐行 UPDATE", old_c_once, repeat=20)
    new_c = bench("新: 单条 UPDATE（计算下推数据库）", new_c_once, repeat=20)

    print("\n=== 汇总 ===")
    for name, old, new in [("A 列过滤", old_a, new_a),
                           ("B N+1 消除", old_b, new_b),
                           ("C 超时检查", old_c, new_c)]:
        if old > 0:
            print(f"  {name:<12} {old:>7.2f} ms → {new:>6.2f} ms，"
                  f"提升 {(1 - new / old) * 100:.0f}%")

    db.close()
    os.remove(BENCH_DB)


if __name__ == "__main__":
    main()
