#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查询失败用例的最近执行记录
用法: python get_failed_case_log.py <case_name>
"""
import sys
import os
import yaml
import sqlite3


def main():
    if len(sys.argv) < 2:
        print("用法: python get_failed_case_log.py <case_name>")
        sys.exit(1)

    case_name = sys.argv[1]

    # 定位配置文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 从 .trae/skills/fix-failed-case/scripts/ 回退到项目根目录
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
    config_path = os.path.join(project_root, 'config', 'execution_config.yaml')

    if not os.path.exists(config_path):
        print(f"ERROR: 配置文件不存在: {config_path}")
        sys.exit(1)

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    db_config = config.get('database', {})
    backend = db_config.get('backend', 'sqlite')

    if backend == 'sqlite':
        _query_sqlite(db_config, case_name, project_root)
    else:
        _query_mysql(db_config, case_name)


def _query_sqlite(db_config, case_name, project_root):
    db_path = db_config.get('sqlite_path', 'data/test_results.db')
    if not os.path.isabs(db_path):
        db_path = os.path.join(project_root, db_path)

    if not os.path.exists(db_path):
        print(f"ERROR: 数据库文件不存在: {db_path}")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM test_case_result WHERE case_name LIKE ? AND status='failed' ORDER BY id DESC LIMIT 1",
            (f"%{case_name}%",)
        )
        row = cursor.fetchone()
        _print_result(row)
    except Exception as e:
        print(f"ERROR: 查询失败: {e}")
        sys.exit(1)
    finally:
        conn.close()


def _query_mysql(db_config, case_name):
    try:
        import pymysql
    except ImportError:
        print("ERROR: pymysql 未安装，无法连接 MySQL")
        sys.exit(1)

    conn = pymysql.connect(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config.get('password', ''),
        database=db_config['database_name'],
        charset=db_config.get('charset', 'utf8mb4'),
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT * FROM test_case_result WHERE case_name LIKE %s AND status='failed' ORDER BY id DESC LIMIT 1",
            (f"%{case_name}%",)
        )
        row = cursor.fetchone()
        _print_result(row)
    except Exception as e:
        print(f"ERROR: 查询失败: {e}")
        sys.exit(1)
    finally:
        conn.close()


def _print_result(row):
    if not row:
        print("NO_FAILED_RECORD")
        return

    if isinstance(row, dict):
        data = row
    else:
        data = dict(row)

    print(f"CASE_NAME: {data.get('case_name', '')}")
    print(f"STATUS: {data.get('status', '')}")
    print(f"DURATION: {data.get('duration', '')}")
    print(f"CREATED_AT: {data.get('created_at', '')}")
    print(f"PROJECT: {data.get('project', '')}")
    print(f"\nERROR_MESSAGE:\n{data.get('error_message', '') or '(空)'}")
    print(f"\nLOG:\n{data.get('log', '') or '(空)'}")


if __name__ == '__main__':
    main()
