"""
SQLite 数据同步到 MySQL 脚本

将本地 SQLite（test_results.db）中的 test_case_info、test_execution、test_case_result
三张表的数据同步到指定的 MySQL 数据库，对应表名为：
  - uitest_test_case_info
  - uitest_test_execution
  - uitest_test_case_result

MySQL 表使用 UUID 主键，并通过 case_id / execution_id / result_id 字段记录源端 id，
避免不同项目合并时 id 冲突。

用法：
    python sync_to_mysql.py <project>

参数：
    project  项目名称，同步前会删除 MySQL 三张表中 project 等于该值的数据，再插入
"""
import argparse
import os
import sys
import uuid
import sqlite3
from datetime import datetime

import pymysql

# ============================================================
# 配置区域（按需修改）
# ============================================================

# SQLite 数据库路径（绝对路径）
SQLITE_PATH = r"D:\UIProject\auto_ui_wts\playwright-ui-automation\data\test_results.db"

# MySQL 连接信息
MYSQL_CONFIG = {
    "host": "10.52.54.101",
    "port": 3306,
    "user": "root",
    "password": "Password123@mysql",
    "database": "qm",
    "charset": "utf8mb4",
    "connect_timeout": 30,
}


# ============================================================
# 建表 SQL
# ============================================================

CREATE_UITEST_TEST_CASE_INFO = """
CREATE TABLE IF NOT EXISTS uitest_test_case_info (
    id          VARCHAR(36)   PRIMARY KEY,
    case_id     INT,
    case_name   VARCHAR(100),
    ms_id       VARCHAR(50),
    project     VARCHAR(100),
    module      VARCHAR(100),
    type        INT,
    update_date DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""

CREATE_UITEST_TEST_EXECUTION = """
CREATE TABLE IF NOT EXISTS uitest_test_execution (
    id            VARCHAR(36)   PRIMARY KEY,
    execution_id  INT,
    start_time    DATETIME,
    end_time      DATETIME,
    total_cases   INT,
    passed_cases  INT,
    failed_cases  INT,
    status        VARCHAR(20),
    duration      FLOAT,
    project       VARCHAR(100),
    module        VARCHAR(100),
    `case`        VARCHAR(100),
    update_date   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""

CREATE_UITEST_TEST_CASE_RESULT = """
CREATE TABLE IF NOT EXISTS uitest_test_case_result (
    id            VARCHAR(36)   PRIMARY KEY,
    result_id     INT,
    execution_id  INT,
    case_name     VARCHAR(500),
    status        VARCHAR(20),
    duration      FLOAT,
    project       VARCHAR(100),
    update_date   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""


def log(msg: str):
    """简单日志输出"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")


# ============================================================
# SQLite 读取
# ============================================================

def get_sqlite_rows(sqlite_path: str, table_name: str, columns: str = "*"):
    """读取 SQLite 指定表的所有数据，返回 list[dict]"""
    if not os.path.exists(sqlite_path):
        log(f"SQLite 数据库文件不存在: {sqlite_path}")
        return []

    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT {columns} FROM {table_name}")
        rows = [dict(row) for row in cursor.fetchall()]
        log(f"SQLite {table_name} 读取到 {len(rows)} 条数据")
        return rows
    except Exception as e:
        log(f"读取 SQLite {table_name} 失败: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


# ============================================================
# MySQL 建表
# ============================================================

def ensure_mysql_tables(mysql_conn):
    """确保 MySQL 中三张目标表存在，不存在则创建"""
    cursor = mysql_conn.cursor()
    try:
        cursor.execute(CREATE_UITEST_TEST_CASE_INFO)
        cursor.execute(CREATE_UITEST_TEST_EXECUTION)
        cursor.execute(CREATE_UITEST_TEST_CASE_RESULT)
        mysql_conn.commit()
        log("MySQL 目标表检查/创建完成")
    finally:
        cursor.close()


def delete_project_data(mysql_conn, project: str):
    """删除 MySQL 三张目标表中 project 等于指定值的数据"""
    cursor = mysql_conn.cursor()
    try:
        cursor.execute("DELETE FROM uitest_test_case_result WHERE project = %s", (project,))
        cursor.execute("DELETE FROM uitest_test_execution WHERE project = %s", (project,))
        cursor.execute("DELETE FROM uitest_test_case_info WHERE project = %s", (project,))
        mysql_conn.commit()
        log(f"MySQL 目标表中 project='{project}' 的数据已删除")
    finally:
        cursor.close()


# ============================================================
# 同步逻辑
# ============================================================

def sync_case_info(mysql_conn, sqlite_rows):
    """同步 test_case_info -> uitest_test_case_info"""
    if not sqlite_rows:
        return
    cursor = mysql_conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    inserted = 0
    try:
        for row in sqlite_rows:
            new_id = str(uuid.uuid4())
            try:
                cursor.execute(
                    """
                    INSERT INTO uitest_test_case_info
                        (id, case_id, case_name, ms_id, project, module, type, update_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        new_id,
                        row.get('id'),
                        row.get('case_name'),
                        row.get('ms_id'),
                        row.get('project'),
                        row.get('module'),
                        row.get('type'),
                        now,
                    ),
                )
                inserted += 1
            except Exception as e:
                log(f"插入 uitest_test_case_info 失败 (case_name={row.get('case_name')}): {e}")
        mysql_conn.commit()
        log(f"uitest_test_case_info 同步完成，成功 {inserted}/{len(sqlite_rows)} 条")
    finally:
        cursor.close()


def sync_execution(mysql_conn, sqlite_rows):
    """同步 test_execution -> uitest_test_execution"""
    if not sqlite_rows:
        return
    cursor = mysql_conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    inserted = 0
    try:
        for row in sqlite_rows:
            new_id = str(uuid.uuid4())
            try:
                cursor.execute(
                    """
                    INSERT INTO uitest_test_execution
                        (id, execution_id, start_time, end_time, total_cases,
                         passed_cases, failed_cases, status, duration,
                         project, module, `case`, update_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        new_id,
                        row.get('id'),
                        row.get('start_time'),
                        row.get('end_time'),
                        row.get('total_cases'),
                        row.get('passed_cases'),
                        row.get('failed_cases'),
                        row.get('status'),
                        row.get('duration'),
                        row.get('project'),
                        row.get('module'),
                        row.get('case'),
                        now,
                    ),
                )
                inserted += 1
            except Exception as e:
                log(f"插入 uitest_test_execution 失败 (execution_id={row.get('id')}): {e}")
        mysql_conn.commit()
        log(f"uitest_test_execution 同步完成，成功 {inserted}/{len(sqlite_rows)} 条")
    finally:
        cursor.close()


def sync_case_result(mysql_conn, sqlite_rows):
    """同步 test_case_result -> uitest_test_case_result"""
    if not sqlite_rows:
        return
    cursor = mysql_conn.cursor()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    inserted = 0
    try:
        for row in sqlite_rows:
            new_id = str(uuid.uuid4())
            try:
                cursor.execute(
                    """
                    INSERT INTO uitest_test_case_result
                        (id, result_id, execution_id, case_name, status,
                         duration, project, update_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        new_id,
                        row.get('id'),
                        row.get('execution_id'),
                        row.get('case_name'),
                        row.get('status'),
                        row.get('duration'),
                        row.get('project'),
                        now,
                    ),
                )
                inserted += 1
            except Exception as e:
                log(f"插入 uitest_test_case_result 失败 (result_id={row.get('id')}): {e}")
        mysql_conn.commit()
        log(f"uitest_test_case_result 同步完成，成功 {inserted}/{len(sqlite_rows)} 条")
    finally:
        cursor.close()


# ============================================================
# 主流程
# ============================================================

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="同步 SQLite 数据到 MySQL")
    parser.add_argument("project", help="项目名称，同步前删除 MySQL 三张表中 project 等于该值的数据")
    args = parser.parse_args()
    project = args.project

    log("=" * 60)
    log("开始同步 SQLite -> MySQL")
    log(f"SQLite 路径: {SQLITE_PATH}")
    log(f"MySQL: {MYSQL_CONFIG['host']}:{MYSQL_CONFIG['port']}/{MYSQL_CONFIG['database']}")
    log(f"项目: {project}")
    log("=" * 60)

    # 1. 读取 SQLite 数据
    case_info_rows = get_sqlite_rows(SQLITE_PATH, "test_case_info")
    execution_rows = get_sqlite_rows(SQLITE_PATH, "test_execution")
    case_result_rows = get_sqlite_rows(SQLITE_PATH, "test_case_result")

    total = len(case_info_rows) + len(execution_rows) + len(case_result_rows)
    if total == 0:
        log("SQLite 中无数据可同步，退出")
        return

    # 2. 连接 MySQL
    try:
        mysql_conn = pymysql.connect(**MYSQL_CONFIG)
        log("MySQL 连接成功")
    except Exception as e:
        log(f"MySQL 连接失败: {e}")
        sys.exit(1)

    # 3. 确保目标表存在
    try:
        ensure_mysql_tables(mysql_conn)
    except Exception as e:
        log(f"MySQL 建表失败: {e}")
        mysql_conn.close()
        sys.exit(1)

    # 4. 删除目标表中该项目的数据
    try:
        delete_project_data(mysql_conn, project)
    except Exception as e:
        log(f"MySQL 删除项目数据失败: {e}")
        mysql_conn.close()
        sys.exit(1)

    # 5. 同步三张表
    try:
        sync_case_info(mysql_conn, case_info_rows)
        sync_execution(mysql_conn, execution_rows)
        sync_case_result(mysql_conn, case_result_rows)
        log("=" * 60)
        log("同步全部完成")
        log("=" * 60)
    except Exception as e:
        log(f"同步过程中出错: {e}")
        sys.exit(1)
    finally:
        mysql_conn.close()


if __name__ == "__main__":
    main()
