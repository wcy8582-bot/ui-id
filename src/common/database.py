"""
数据库操作类
提供测试结果的数据库存储功能
支持 MySQL 和 SQLite 两种后端，通过配置文件切换
"""
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional, Any
from src.common.logger import logger

try:
    import pymysql
    from pymysql import err as pymysql_err
    PYMYSQL_AVAILABLE = True
except ImportError:
    PYMYSQL_AVAILABLE = False


class DatabaseError(Exception):
    """数据库操作异常"""
    pass


def _dict_factory(cursor, row):
    """SQLite 行工厂，将行转为字典"""
    columns = [col[0] for col in cursor.description]
    return dict(zip(columns, row))


class SQLiteDatabaseBackend:
    """SQLite 数据库后端"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    def connect(self) -> bool:
        try:
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)

            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = _dict_factory
            self.connection.execute("PRAGMA journal_mode=WAL")
            self.connection.execute("PRAGMA foreign_keys=ON")
            logger.info(f"SQLite 数据库连接成功: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"SQLite 数据库连接失败: {e}")
            return False

    def close(self):
        if self.connection:
            try:
                self.connection.close()
                logger.info("SQLite 数据库连接已关闭")
            except:
                pass

    def create_tables(self) -> bool:
        if not self.connection:
            logger.error("未建立数据库连接")
            return False

        # 先独立创建测试计划相关表（带独立提交），避免受历史表结构漂移导致的建表失败影响
        self.create_plan_tables()

        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_execution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    total_cases INTEGER NOT NULL DEFAULT 0,
                    passed_cases INTEGER NOT NULL DEFAULT 0,
                    failed_cases INTEGER NOT NULL DEFAULT 0,
                    status VARCHAR(20) NOT NULL DEFAULT 'running',
                    duration FLOAT DEFAULT NULL,
                    command VARCHAR(500) NOT NULL,
                    project VARCHAR(100),
                    module VARCHAR(100),
                    `case` VARCHAR(100),
                    version VARCHAR(50),
                    timeout_minutes INTEGER DEFAULT 30,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_case_result (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    execution_id INTEGER NOT NULL,
                    case_name VARCHAR(500) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    duration FLOAT NOT NULL,
                    log TEXT NOT NULL,
                    error_message TEXT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    project VARCHAR(100)
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_case_execution_id ON test_case_result(execution_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_case_status ON test_case_result(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_case_project ON test_case_result(project)')

            # test_execution 补索引：status（超时扫描）+ start_time（时间范围裁剪）
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_exec_status ON test_execution(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_exec_start_time ON test_execution(start_time)')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_case_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_name VARCHAR(100) NOT NULL UNIQUE,
                    case_scene VARCHAR(500),
                    ms_id VARCHAR(50),
                    project VARCHAR(100),
                    module VARCHAR(100),
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    type INTEGER DEFAULT 1
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ci_case_name ON test_case_info(case_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ci_project ON test_case_info(project)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ci_module ON test_case_info(module)')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version VARCHAR(50) NOT NULL,
                    version_info VARCHAR(500),
                    backup_time DATETIME NOT NULL,
                    backup_user VARCHAR(100) NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tv_version ON test_versions(version)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tv_is_active ON test_versions(is_active)')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fix_failed_case (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project VARCHAR(100),
                    case_name VARCHAR(500) NOT NULL,
                    execution_id INTEGER,
                    error_analysis TEXT,
                    source_code TEXT,
                    fixed_code TEXT,
                    status VARCHAR(20) NOT NULL DEFAULT '进行中',
                    start_time DATETIME,
                    end_time DATETIME,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ffc_case_name ON fix_failed_case(case_name)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ffc_status ON fix_failed_case(status)')

            self.connection.commit()
            logger.info("SQLite 数据库表初始化成功")
            return True
        except Exception as e:
            logger.error(f"SQLite 创建表失败: {e}")
            return False
        finally:
            cursor.close()

    def create_plan_tables(self) -> bool:
        """独立创建测试计划相关表（自带提交），与历史表初始化解耦

        同时为 test_execution 补充 plan_id / plan_name 列（老库兼容）。
        """
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_plan (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_name VARCHAR(200) NOT NULL UNIQUE,
                    description VARCHAR(500),
                    creator VARCHAR(100),
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tp_is_active ON test_plan(is_active)')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_plan_case (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plan_id INTEGER NOT NULL,
                    case_name VARCHAR(100) NOT NULL
                )
            ''')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_tpc_plan_id ON test_plan_case(plan_id)')
            # 兼容老库：为 test_execution 补充 plan_id / plan_name 列
            self._safe_add_column(cursor, 'test_execution', 'plan_id', 'INTEGER')
            self._safe_add_column(cursor, 'test_execution', 'plan_name', 'VARCHAR(200)')
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"SQLite 创建测试计划表失败: {e}")
            return False
        finally:
            cursor.close()

    def _safe_add_column(self, cursor, table: str, column: str, col_type: str):
        """为已存在的表安全添加列，列已存在则忽略"""
        try:
            cursor.execute(f'ALTER TABLE {table} ADD COLUMN {column} {col_type}')
            logger.info(f"已为表 {table} 添加列 {column}")
        except Exception:
            # 列已存在或其他情况，忽略
            pass

    def drop_tables(self):
        if not self.connection:
            return
        cursor = self.connection.cursor()
        try:
            cursor.execute('DROP TABLE IF EXISTS fix_failed_case')
            cursor.execute('DROP TABLE IF EXISTS test_case_result')
            cursor.execute('DROP TABLE IF EXISTS test_case_info')
            cursor.execute('DROP TABLE IF EXISTS test_versions')
            cursor.execute('DROP TABLE IF EXISTS test_plan_case')
            cursor.execute('DROP TABLE IF EXISTS test_plan')
            cursor.execute('DROP TABLE IF EXISTS test_execution')
            self.connection.commit()
        finally:
            cursor.close()

    def update_execution_total_cases(self, execution_id: int, total_cases: int) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE test_execution SET total_cases = ?, updated_at = ?
                WHERE id = ?
            ''', (total_cases, now, execution_id))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"更新总用例数失败: {e}")
            return False
        finally:
            cursor.close()

    def update_execution_complete(self, execution_id: int, total_cases: int,
                                   passed_cases: int, status: str = 'completed') -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            end_time = datetime.now()
            failed_cases = total_cases - passed_cases

            cursor.execute("SELECT start_time FROM test_execution WHERE id = ?", (execution_id,))
            result = cursor.fetchone()
            if result:
                start_time = result['start_time']
                if isinstance(start_time, str):
                    start_time = datetime.fromisoformat(start_time)
                duration = (end_time - start_time).total_seconds()
            else:
                duration = 0

            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE test_execution
                SET end_time = ?, total_cases = ?, passed_cases = ?,
                    failed_cases = ?, status = ?, duration = ?, updated_at = ?
                WHERE id = ?
            ''', (end_time, total_cases, passed_cases, failed_cases, status, duration, now, execution_id))
            self.connection.commit()
            logger.info(f"执行记录已更新，ID: {execution_id}, 状态: {status}")
            return True
        except Exception as e:
            logger.error(f"更新执行记录失败: {e}")
            return False
        finally:
            cursor.close()

    def update_execution_timeout(self, execution_id: int) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            end_time = datetime.now()
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE test_execution SET end_time = ?, status = 'timeout', updated_at = ?
                WHERE id = ?
            ''', (end_time, now, execution_id))
            self.connection.commit()
            logger.info(f"执行记录已标记为超时，ID: {execution_id}")
            return True
        except Exception as e:
            logger.error(f"更新执行记录失败: {e}")
            return False
        finally:
            cursor.close()

    def check_and_update_timeout_executions(self) -> int:
        """单条 UPDATE 完成超时标记：计算下推到数据库，避免 查N行→逐行UPDATE 的 N+1 次往返。

        利用每行自己的 timeout_minutes 做动态时间裁剪：
          start_time < 当前时间 - timeout_minutes 分钟
        """
        if not self.connection:
            return 0
        cursor = self.connection.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE test_execution
                SET end_time = ?, status = 'timeout', updated_at = ?
                WHERE status = 'running'
                  AND start_time < datetime('now', 'localtime', '-' || timeout_minutes || ' minutes')
            ''', (now, now))
            updated_count = cursor.rowcount
            self.connection.commit()
            if updated_count > 0:
                logger.info(f"已标记 {updated_count} 条超时记录")
            return updated_count
        except Exception as e:
            logger.error(f"检查超时记录失败: {e}")
            return 0
        finally:
            cursor.close()

    def insert_case_result(self, execution_id: int, case_name: str,
                          status: str, duration: float, log: str,
                          error_message: str = None, project: str = None) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            log = log if log else ""
            cursor.execute('''
                INSERT INTO test_case_result
                (execution_id, case_name, status, duration, log, error_message, project)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (execution_id, case_name, status, duration, log, error_message, project))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"插入用例结果失败: {e}")
            return False
        finally:
            cursor.close()

    def batch_insert_case_results(self, execution_id: int, results: List[Dict], project: str = None) -> int:
        if not self.connection:
            return 0
        cursor = self.connection.cursor()
        saved_count = 0
        try:
            for result in results:
                log = result.get('log', '')
                params = (
                    execution_id,
                    result['case_name'],
                    result['status'],
                    result['duration'],
                    log,
                    result.get('error_message'),
                    result.get('project', project)
                )
                try:
                    cursor.execute('''
                        INSERT INTO test_case_result
                        (execution_id, case_name, status, duration, log, error_message, project)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', params)
                    saved_count += 1
                except Exception as e:
                    logger.error(f"插入用例 {result['case_name']} 失败: {e}")
            self.connection.commit()
            logger.info(f"批量插入完成，成功 {saved_count}/{len(results)} 条")
            return saved_count
        finally:
            cursor.close()

    def get_execution_by_id(self, execution_id: int) -> Optional[Dict]:
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM test_execution WHERE id = ?", (execution_id,))
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"查询执行记录失败: {e}")
            return None
        finally:
            cursor.close()

    def get_recent_executions(self, limit: int = 10) -> List[Dict]:
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"SELECT * FROM test_execution ORDER BY id DESC LIMIT {limit}")
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"查询执行记录失败: {e}")
            return []
        finally:
            cursor.close()

    def get_case_results_by_execution(self, execution_id: int) -> List[Dict]:
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM test_case_result WHERE execution_id = ? ORDER BY id", (execution_id,))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"查询用例结果失败: {e}")
            return []
        finally:
            cursor.close()

    def get_case_results_summary(self, execution_id: int) -> List[Dict]:
        """列过滤版结果查询：报告页/列表页不需要 log 大字段，显式列裁剪。

        log 列单条可达几十KB，SELECT * 会把它全部加载进内存；
        日志通过 /get_case_log 接口按需单条获取。
        """
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                SELECT id, execution_id, case_name, status, duration,
                       error_message, created_at, project
                FROM test_case_result WHERE execution_id = ? ORDER BY id
            ''', (execution_id,))
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"查询用例结果摘要失败: {e}")
            return []
        finally:
            cursor.close()

    def get_case_info_map(self, case_names: List[str]) -> Dict[str, Dict]:
        """批量查询用例信息，一次 IN 查询替代逐条查询（消除 N+1）。

        返回 {case_name: case_info} 映射，查不到的用例不在字典中。
        """
        if not self.connection or not case_names:
            return {}
        cursor = self.connection.cursor()
        try:
            placeholders = ','.join(['?'] * len(case_names))
            cursor.execute(
                f"SELECT * FROM test_case_info WHERE case_name IN ({placeholders})",
                tuple(case_names))
            return {row['case_name']: row for row in cursor.fetchall()}
        except Exception as e:
            logger.error(f"批量查询用例信息失败: {e}")
            return {}
        finally:
            cursor.close()

    def get_failed_cases(self, limit: int = 50) -> List[Dict]:
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute(f'''
                SELECT c.id, c.execution_id, c.case_name, c.status,
                       c.duration, c.error_message, c.created_at, c.project,
                       e.start_time as execution_time
                FROM test_case_result c
                JOIN test_execution e ON c.execution_id = e.id
                WHERE c.status = 'failed'
                ORDER BY c.id DESC
                LIMIT {limit}
            ''')
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"查询失败用例失败: {e}")
            return []
        finally:
            cursor.close()

    def get_statistics(self) -> Optional[Dict]:
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                SELECT
                    COUNT(*) as total_executions,
                    SUM(total_cases) as total_cases,
                    SUM(passed_cases) as total_passed,
                    SUM(failed_cases) as total_failed,
                    ROUND(SUM(passed_cases) * 100.0 / SUM(total_cases), 2) as success_rate
                FROM test_execution
            ''')
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"查询统计信息失败: {e}")
            return None
        finally:
            cursor.close()

    def insert_or_update_case_info(self, case_name: str, case_scene: str = None,
                                  ms_id: str = None, project: str = None,
                                  module: str = None, type: int = 1) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("SELECT id FROM test_case_info WHERE case_name = ?", (case_name,))
            existing = cursor.fetchone()
            if existing:
                cursor.execute('''
                    UPDATE test_case_info
                    SET case_scene = ?, ms_id = ?, project = ?, module = ?, type = ?, updated_at = ?
                    WHERE case_name = ?
                ''', (case_scene, ms_id, project, module, type, now, case_name))
            else:
                cursor.execute('''
                    INSERT INTO test_case_info (case_name, case_scene, ms_id, project, module, type)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (case_name, case_scene, ms_id, project, module, type))
            self.connection.commit()
            logger.info(f"用例信息已保存/更新: {case_name}")
            return True
        except Exception as e:
            logger.error(f"保存用例信息失败: {e}")
            return False
        finally:
            cursor.close()

    def clear_case_info_table(self) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM test_case_info")
            self.connection.commit()
            logger.info("用例信息表已清空")
            return True
        except Exception as e:
            logger.error(f"清空用例信息表失败: {e}")
            return False
        finally:
            cursor.close()

    def batch_insert_case_info(self, case_list: List[Dict]) -> int:
        if not self.connection:
            return 0
        cursor = self.connection.cursor()
        success_count = 0
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for case_info in case_list:
                try:
                    cursor.execute("SELECT id FROM test_case_info WHERE case_name = ?",
                                   (case_info.get('case_name'),))
                    existing = cursor.fetchone()
                    if existing:
                        cursor.execute('''
                            UPDATE test_case_info
                            SET case_scene = ?, ms_id = ?, project = ?, module = ?, type = ?, updated_at = ?
                            WHERE case_name = ?
                        ''', (case_info.get('case_scene'), case_info.get('ms_id'),
                              case_info.get('project'), case_info.get('module'),
                              case_info.get('type', 1), now, case_info.get('case_name')))
                    else:
                        cursor.execute('''
                            INSERT INTO test_case_info (case_name, case_scene, ms_id, project, module, type)
                            VALUES (?, ?, ?, ?, ?, ?)
                        ''', (case_info.get('case_name'), case_info.get('case_scene'),
                              case_info.get('ms_id'), case_info.get('project'),
                              case_info.get('module'), case_info.get('type', 1)))
                    success_count += 1
                except Exception as e:
                    logger.error(f"保存用例信息失败 {case_info.get('case_name')}: {e}")
            self.connection.commit()
            logger.info(f"批量保存用例信息完成，成功 {success_count}/{len(case_list)} 条")
            return success_count
        finally:
            cursor.close()

    def get_case_info_by_name(self, case_name: str) -> Optional[Dict]:
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM test_case_info WHERE case_name = ?", (case_name,))
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"查询用例信息失败: {e}")
            return None
        finally:
            cursor.close()

    def get_all_case_info(self) -> List[Dict]:
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM test_case_info ORDER BY project, module, case_name")
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"查询用例信息失败: {e}")
            return []
        finally:
            cursor.close()

    def get_active_version(self, version: str) -> Optional[Dict]:
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                SELECT version, version_info, backup_time, backup_user, created_at, updated_at
                FROM test_versions
                WHERE version = ? AND is_active = 1
            ''', (version,))
            result = cursor.fetchone()
            if result:
                logger.info(f"找到有效版本: {version}")
                return {
                    "version": result['version'],
                    "version_info": result['version_info'],
                    "backup_time": result['backup_time'],
                    "backup_user": result['backup_user'],
                    "created_at": result['created_at'],
                    "updated_at": result['updated_at']
                }
            return None
        except Exception as e:
            logger.error(f"查询版本信息失败: {e}")
            return None
        finally:
            cursor.close()

    def insert_or_update_version(self, version: str, backup_user: str,
                               version_info: str = None) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            existing = self.get_active_version(version)
            if existing:
                cursor.execute('''
                    UPDATE test_versions
                    SET version_info = ?, backup_time = ?, backup_user = ?, updated_at = ?
                    WHERE version = ? AND is_active = 1
                ''', (version_info, datetime.now(), backup_user, now, version))
                logger.info(f"版本 {version} 已更新")
            else:
                cursor.execute('''
                    INSERT INTO test_versions
                    (version, version_info, backup_time, backup_user, is_active)
                    VALUES (?, ?, ?, ?, 1)
                ''', (version, version_info, datetime.now(), backup_user))
                logger.info(f"版本 {version} 已创建")
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"保存版本信息失败: {e}")
            return False
        finally:
            cursor.close()

    def mark_version_deleted(self, version: str) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE test_versions SET is_active = 0, updated_at = ?
                WHERE version = ? AND is_active = 1
            ''', (now, version))
            self.connection.commit()
            logger.info(f"版本 {version} 已标记为删除")
            return True
        except Exception as e:
            logger.error(f"标记版本删除失败: {e}")
            return False
        finally:
            cursor.close()

    def get_all_active_versions(self) -> List[Dict]:
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                SELECT version, version_info, backup_time, backup_user, created_at, updated_at
                FROM test_versions
                WHERE is_active = 1
                ORDER BY updated_at DESC
            ''')
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"查询版本列表失败: {e}")
            return []
        finally:
            cursor.close()

    def insert_execution_start(self, command: str, project: str = None,
                               module: str = None, case: str = None,
                               timeout_minutes: int = 30, version: str = None,
                               plan_id: int = None, plan_name: str = None) -> int:
        if not self.connection:
            return -1
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO test_execution
                (start_time, status, command, project, module, `case`, version, timeout_minutes, plan_id, plan_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (datetime.now(), 'running', command, project, module, case, version,
                  timeout_minutes, plan_id, plan_name))
            self.connection.commit()
            execution_id = cursor.lastrowid
            logger.info(f"执行记录已创建，ID: {execution_id}")
            return execution_id
        except Exception as e:
            logger.error(f"插入执行记录失败: {e}")
            return -1
        finally:
            cursor.close()

    # ==================== 测试计划相关（SQLite） ====================

    def create_plan(self, plan_name: str, description: str = None,
                    creator: str = None) -> int:
        if not self.connection:
            return -1
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO test_plan (plan_name, description, creator, is_active)
                VALUES (?, ?, ?, 1)
            ''', (plan_name, description, creator))
            self.connection.commit()
            plan_id = cursor.lastrowid
            logger.info(f"测试计划已创建，ID: {plan_id}, 名称: {plan_name}")
            return plan_id
        except Exception as e:
            logger.error(f"创建测试计划失败: {e}")
            return -1
        finally:
            cursor.close()

    def get_all_plans(self) -> List[Dict]:
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                SELECT p.*,
                    (SELECT COUNT(*) FROM test_plan_case c WHERE c.plan_id = p.id) as case_count
                FROM test_plan p
                WHERE p.is_active = 1
                ORDER BY p.id DESC
            ''')
            return cursor.fetchall()
        except Exception as e:
            logger.error(f"查询测试计划列表失败: {e}")
            return []
        finally:
            cursor.close()

    def get_plan_by_id(self, plan_id: int) -> Optional[Dict]:
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM test_plan WHERE id = ? AND is_active = 1", (plan_id,))
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"查询测试计划失败: {e}")
            return None
        finally:
            cursor.close()

    def get_plan_by_name(self, plan_name: str) -> Optional[Dict]:
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM test_plan WHERE plan_name = ? AND is_active = 1", (plan_name,))
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"查询测试计划失败: {e}")
            return None
        finally:
            cursor.close()

    def get_cases_by_plan(self, plan_id: int) -> List[str]:
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT case_name FROM test_plan_case WHERE plan_id = ?", (plan_id,))
            return [row['case_name'] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"查询计划用例失败: {e}")
            return []
        finally:
            cursor.close()

    def update_plan_cases(self, plan_id: int, case_names: List[str]) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("DELETE FROM test_plan_case WHERE plan_id = ?", (plan_id,))
            for case_name in case_names:
                cursor.execute("INSERT INTO test_plan_case (plan_id, case_name) VALUES (?, ?)",
                               (plan_id, case_name))
            cursor.execute("UPDATE test_plan SET updated_at = ? WHERE id = ?", (now, plan_id))
            self.connection.commit()
            logger.info(f"计划 {plan_id} 用例已更新，共 {len(case_names)} 条")
            return True
        except Exception as e:
            logger.error(f"更新计划用例失败: {e}")
            return False
        finally:
            cursor.close()

    def update_plan_desc(self, plan_id: int, description: str) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("UPDATE test_plan SET description = ?, updated_at = ? WHERE id = ?",
                           (description, now, plan_id))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"更新计划描述失败: {e}")
            return False
        finally:
            cursor.close()

    def delete_plan(self, plan_id: int) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            # 真删除：先删关联用例，再删计划主记录
            cursor.execute("DELETE FROM test_plan_case WHERE plan_id = ?", (plan_id,))
            cursor.execute("DELETE FROM test_plan WHERE id = ?", (plan_id,))
            self.connection.commit()
            logger.info(f"测试计划已删除（物理删除），ID: {plan_id}")
            return True
        except Exception as e:
            logger.error(f"删除测试计划失败: {e}")
            return False
        finally:
            cursor.close()

    # ==================== 用例修复任务相关（SQLite） ====================

    def insert_fix_task(self, project: str, case_name: str, execution_id: int,
                        source_code: str) -> int:
        if not self.connection:
            return -1
        cursor = self.connection.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO fix_failed_case
                (project, case_name, execution_id, source_code, status, start_time)
                VALUES (?, ?, ?, ?, '进行中', ?)
            ''', (project, case_name, execution_id, source_code, now))
            self.connection.commit()
            task_id = cursor.lastrowid
            logger.info(f"用例修复任务已创建，ID: {task_id}")
            return task_id
        except Exception as e:
            logger.error(f"创建用例修复任务失败: {e}")
            return -1
        finally:
            cursor.close()

    def update_fix_task_result(self, task_id: int, error_analysis: str,
                               fixed_code: str, status: str = '已完成') -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE fix_failed_case
                SET error_analysis = ?, fixed_code = ?, status = ?, end_time = ?
                WHERE id = ?
            ''', (error_analysis, fixed_code, status, now, task_id))
            self.connection.commit()
            logger.info(f"用例修复任务已更新，ID: {task_id}, 状态: {status}")
            return True
        except Exception as e:
            logger.error(f"更新用例修复任务失败: {e}")
            return False
        finally:
            cursor.close()

    def update_fix_task_status(self, task_id: int, status: str) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE fix_failed_case SET status = ?, end_time = ? WHERE id = ?
            ''', (status, now, task_id))
            self.connection.commit()
            logger.info(f"用例修复任务状态已更新，ID: {task_id}, 状态: {status}")
            return True
        except Exception as e:
            logger.error(f"更新用例修复任务状态失败: {e}")
            return False
        finally:
            cursor.close()

    def get_fix_task(self, task_id: int) -> Optional[Dict]:
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM fix_failed_case WHERE id = ?", (task_id,))
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"查询用例修复任务失败: {e}")
            return None
        finally:
            cursor.close()

    def get_fix_task_by_case(self, project: str, case_name: str,
                             execution_id: int) -> Optional[Dict]:
        """根据项目、用例名称、执行ID查询最新一条修复任务"""
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                SELECT * FROM fix_failed_case
                WHERE project = ? AND case_name = ? AND execution_id = ?
                ORDER BY id DESC LIMIT 1
            ''', (project, case_name, execution_id))
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"查询用例修复任务失败: {e}")
            return None
        finally:
            cursor.close()

    def reset_fix_task(self, task_id: int) -> bool:
        """重置修复任务为进行中：清空结果、结束时间，更新开始时间"""
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE fix_failed_case
                SET status = '进行中', error_analysis = NULL, fixed_code = NULL,
                    end_time = NULL, start_time = ?
                WHERE id = ?
            ''', (now, task_id))
            self.connection.commit()
            logger.info(f"用例修复任务已重置，ID: {task_id}")
            return True
        except Exception as e:
            logger.error(f"重置用例修复任务失败: {e}")
            return False
        finally:
            cursor.close()


class MySQLDatabaseBackend:
    """MySQL 数据库后端"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None

    def connect(self) -> bool:
        if not PYMYSQL_AVAILABLE:
            logger.error("pymysql 未安装")
            return False
        try:
            self.connection = pymysql.connect(
                host=self.config['host'],
                port=self.config['port'],
                user=self.config['user'],
                password=self.config.get('password', ''),
                database=self.config['database_name'],
                charset=self.config.get('charset', 'utf8mb4'),
                connect_timeout=self.config.get('connect_timeout', 30),
                cursorclass=pymysql.cursors.DictCursor
            )
            logger.info(f"数据库连接成功: {self.config['host']}:{self.config['port']}/{self.config['database_name']}")
            return True
        except pymysql_err.OperationalError as e:
            logger.error(f"数据库连接失败: {e}")
            return False

    def close(self):
        if self.connection:
            try:
                self.connection.close()
                logger.info("数据库连接已关闭")
            except:
                pass

    def create_tables(self) -> bool:
        if not self.connection:
            return False
        # 先独立创建测试计划相关表，避免受历史表结构漂移影响
        self.create_plan_tables()
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_execution (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    start_time DATETIME NOT NULL,
                    end_time DATETIME,
                    total_cases INT NOT NULL DEFAULT 0,
                    passed_cases INT NOT NULL DEFAULT 0,
                    failed_cases INT NOT NULL DEFAULT 0,
                    status VARCHAR(20) NOT NULL DEFAULT 'running',
                    duration FLOAT DEFAULT NULL,
                    command VARCHAR(500) NOT NULL,
                    project VARCHAR(100),
                    module VARCHAR(100),
                    `case` VARCHAR(100),
                    version VARCHAR(50),
                    timeout_minutes INT DEFAULT 30,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_exec_status (status),
                    INDEX idx_exec_start_time (start_time)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_case_result (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    execution_id INT NOT NULL,
                    case_name VARCHAR(500) NOT NULL,
                    status VARCHAR(20) NOT NULL,
                    duration FLOAT NOT NULL,
                    log TEXT NOT NULL,
                    error_message TEXT,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    project VARCHAR(100),
                    INDEX idx_case_execution_id (execution_id),
                    INDEX idx_case_status (status),
                    INDEX idx_case_project (project)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_case_info (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    case_name VARCHAR(100) NOT NULL UNIQUE,
                    case_scene VARCHAR(500),
                    ms_id VARCHAR(50),
                    project VARCHAR(100),
                    module VARCHAR(100),
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    type INTEGER DEFAULT 1,
                    INDEX idx_case_name (case_name),
                    INDEX idx_project (project),
                    INDEX idx_module (module)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_versions (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    version VARCHAR(50) NOT NULL,
                    version_info VARCHAR(500),
                    backup_time DATETIME NOT NULL,
                    backup_user VARCHAR(100) NOT NULL,
                    is_active TINYINT NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_version (version),
                    INDEX idx_is_active (is_active)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fix_failed_case (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    project VARCHAR(100),
                    case_name VARCHAR(500) NOT NULL,
                    execution_id INT,
                    error_analysis TEXT,
                    source_code TEXT,
                    fixed_code TEXT,
                    status VARCHAR(20) NOT NULL DEFAULT '进行中',
                    start_time DATETIME,
                    end_time DATETIME,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_ffc_case_name (case_name),
                    INDEX idx_ffc_status (status)
                )
            ''')

            self.connection.commit()
            logger.info("数据库表初始化成功")
            return True
        except pymysql_err.OperationalError as e:
            logger.error(f"创建表失败: {e}")
            return False
        finally:
            cursor.close()

    def _safe_add_column(self, cursor, table: str, column: str, col_type: str):
        """为已存在的表安全添加列，列已存在则忽略"""
        try:
            cursor.execute(f'ALTER TABLE {table} ADD COLUMN {column} {col_type}')
            logger.info(f"已为表 {table} 添加列 {column}")
        except Exception:
            # 列已存在或其他情况，忽略
            pass

    def create_plan_tables(self) -> bool:
        """独立创建测试计划相关表（自带提交），与历史表初始化解耦

        同时为 test_execution 补充 plan_id / plan_name 列（老库兼容）。
        """
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_plan (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    plan_name VARCHAR(200) NOT NULL UNIQUE,
                    description VARCHAR(500),
                    creator VARCHAR(100),
                    is_active TINYINT NOT NULL DEFAULT 1,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    INDEX idx_tp_is_active (is_active)
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS test_plan_case (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    plan_id INT NOT NULL,
                    case_name VARCHAR(100) NOT NULL,
                    INDEX idx_tpc_plan_id (plan_id)
                )
            ''')
            # 兼容老库：为 test_execution 补充 plan_id / plan_name 列
            self._safe_add_column(cursor, 'test_execution', 'plan_id', 'INT')
            self._safe_add_column(cursor, 'test_execution', 'plan_name', 'VARCHAR(200)')
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"创建测试计划表失败: {e}")
            return False
        finally:
            cursor.close()

    def drop_tables(self):
        if not self.connection:
            return
        cursor = self.connection.cursor()
        try:
            cursor.execute('DROP TABLE IF EXISTS fix_failed_case')
            cursor.execute('DROP TABLE IF EXISTS test_case_result')
            cursor.execute('DROP TABLE IF EXISTS test_case_info')
            cursor.execute('DROP TABLE IF EXISTS test_versions')
            cursor.execute('DROP TABLE IF EXISTS test_plan_case')
            cursor.execute('DROP TABLE IF EXISTS test_plan')
            cursor.execute('DROP TABLE IF EXISTS test_execution')
            self.connection.commit()
        finally:
            cursor.close()

    def update_execution_total_cases(self, execution_id: int, total_cases: int) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                UPDATE test_execution SET total_cases = %s
                WHERE id = %s
            ''', (total_cases, execution_id))
            self.connection.commit()
            return True
        except pymysql_err.OperationalError as e:
            logger.error(f"更新总用例数失败: {e}")
            return False
        finally:
            cursor.close()

    def update_execution_complete(self, execution_id: int, total_cases: int,
                                   passed_cases: int, status: str = 'completed') -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            end_time = datetime.now()
            failed_cases = total_cases - passed_cases
            cursor.execute("SELECT start_time FROM test_execution WHERE id = %s", (execution_id,))
            result = cursor.fetchone()
            if result:
                start_time = result['start_time']
                duration = (end_time - start_time).total_seconds()
            else:
                duration = 0
            cursor.execute('''
                UPDATE test_execution
                SET end_time = %s, total_cases = %s, passed_cases = %s,
                    failed_cases = %s, status = %s, duration = %s
                WHERE id = %s
            ''', (end_time, total_cases, passed_cases, failed_cases, status, duration, execution_id))
            self.connection.commit()
            logger.info(f"执行记录已更新，ID: {execution_id}, 状态: {status}")
            return True
        except pymysql_err.OperationalError as e:
            logger.error(f"更新执行记录失败: {e}")
            return False
        finally:
            cursor.close()

    def update_execution_timeout(self, execution_id: int) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            end_time = datetime.now()
            cursor.execute('''
                UPDATE test_execution SET end_time = %s, status = 'timeout'
                WHERE id = %s
            ''', (end_time, execution_id))
            self.connection.commit()
            logger.info(f"执行记录已标记为超时，ID: {execution_id}")
            return True
        except pymysql_err.OperationalError as e:
            logger.error(f"更新执行记录失败: {e}")
            return False
        finally:
            cursor.close()

    def check_and_update_timeout_executions(self) -> int:
        """单条 UPDATE 完成超时标记：计算下推到数据库，消除 查N行→逐行UPDATE 的往返。

        TIMESTAMPDIFF 在 WHERE 中直接用每行自己的 timeout_minutes 做时间裁剪。
        """
        if not self.connection:
            return 0
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                UPDATE test_execution
                SET end_time = NOW(), status = 'timeout'
                WHERE status = 'running'
                AND TIMESTAMPDIFF(MINUTE, start_time, NOW()) > timeout_minutes
            ''')
            updated_count = cursor.rowcount
            self.connection.commit()
            if updated_count > 0:
                logger.info(f"已标记 {updated_count} 条超时记录")
            return updated_count
        except pymysql_err.OperationalError as e:
            logger.error(f"检查超时记录失败: {e}")
            return 0
        finally:
            cursor.close()

    def insert_case_result(self, execution_id: int, case_name: str,
                          status: str, duration: float, log: str,
                          error_message: str = None, project: str = None) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            log = log if log else ""
            cursor.execute('''
                INSERT INTO test_case_result
                (execution_id, case_name, status, duration, log, error_message, project)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (execution_id, case_name, status, duration, log, error_message, project))
            self.connection.commit()
            return True
        except pymysql_err.OperationalError as e:
            logger.error(f"插入用例结果失败: {e}")
            return False
        finally:
            cursor.close()

    def batch_insert_case_results(self, execution_id: int, results: List[Dict], project: str = None) -> int:
        if not self.connection:
            return 0
        cursor = self.connection.cursor()
        saved_count = 0
        try:
            for result in results:
                log = result.get('log', '')
                params = (execution_id, result['case_name'], result['status'],
                          result['duration'], log, result.get('error_message'),
                          result.get('project', project))
                try:
                    cursor.execute('''
                        INSERT INTO test_case_result
                        (execution_id, case_name, status, duration, log, error_message, project)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ''', params)
                    saved_count += 1
                except pymysql_err.OperationalError as e:
                    logger.error(f"插入用例 {result['case_name']} 失败: {e}")
            self.connection.commit()
            logger.info(f"批量插入完成，成功 {saved_count}/{len(results)} 条")
            return saved_count
        finally:
            cursor.close()

    def get_execution_by_id(self, execution_id: int) -> Optional[Dict]:
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM test_execution WHERE id = %s", (execution_id,))
            return cursor.fetchone()
        except pymysql_err.OperationalError as e:
            logger.error(f"查询执行记录失败: {e}")
            return None
        finally:
            cursor.close()

    def get_recent_executions(self, limit: int = 10) -> List[Dict]:
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute(f"SELECT * FROM test_execution ORDER BY id DESC LIMIT {limit}")
            return cursor.fetchall()
        except pymysql_err.OperationalError as e:
            logger.error(f"查询执行记录失败: {e}")
            return []
        finally:
            cursor.close()

    def get_case_results_by_execution(self, execution_id: int) -> List[Dict]:
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM test_case_result WHERE execution_id = %s ORDER BY id", (execution_id,))
            return cursor.fetchall()
        except pymysql_err.OperationalError as e:
            logger.error(f"查询用例结果失败: {e}")
            return []
        finally:
            cursor.close()

    def get_case_results_summary(self, execution_id: int) -> List[Dict]:
        """列过滤版结果查询：不取 log 大字段，日志走 /get_case_log 按需获取。"""
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                SELECT id, execution_id, case_name, status, duration,
                       error_message, created_at, project
                FROM test_case_result WHERE execution_id = %s ORDER BY id
            ''', (execution_id,))
            return cursor.fetchall()
        except pymysql_err.OperationalError as e:
            logger.error(f"查询用例结果摘要失败: {e}")
            return []
        finally:
            cursor.close()

    def get_case_info_map(self, case_names: List[str]) -> Dict[str, Dict]:
        """批量查询用例信息，一次 IN 查询替代逐条查询（消除 N+1）。"""
        if not self.connection or not case_names:
            return {}
        cursor = self.connection.cursor()
        try:
            placeholders = ','.join(['%s'] * len(case_names))
            cursor.execute(
                f"SELECT * FROM test_case_info WHERE case_name IN ({placeholders})",
                tuple(case_names))
            return {row['case_name']: row for row in cursor.fetchall()}
        except pymysql_err.OperationalError as e:
            logger.error(f"批量查询用例信息失败: {e}")
            return {}
        finally:
            cursor.close()

    def get_failed_cases(self, limit: int = 50) -> List[Dict]:
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute(f'''
                SELECT c.id, c.execution_id, c.case_name, c.status,
                       c.duration, c.error_message, c.created_at, c.project,
                       e.start_time as execution_time
                FROM test_case_result c
                JOIN test_execution e ON c.execution_id = e.id
                WHERE c.status = 'failed'
                ORDER BY c.id DESC
                LIMIT {limit}
            ''')
            return cursor.fetchall()
        except pymysql_err.OperationalError as e:
            logger.error(f"查询失败用例失败: {e}")
            return []
        finally:
            cursor.close()

    def get_statistics(self) -> Optional[Dict]:
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                SELECT
                    COUNT(*) as total_executions,
                    SUM(total_cases) as total_cases,
                    SUM(passed_cases) as total_passed,
                    SUM(failed_cases) as total_failed,
                    ROUND(SUM(passed_cases) * 100.0 / SUM(total_cases), 2) as success_rate
                FROM test_execution
            ''')
            return cursor.fetchone()
        except pymysql_err.OperationalError as e:
            logger.error(f"查询统计信息失败: {e}")
            return None
        finally:
            cursor.close()

    def insert_or_update_case_info(self, case_name: str, case_scene: str = None,
                                  ms_id: str = None, project: str = None,
                                  module: str = None, type: int = 1) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO test_case_info (case_name, case_scene, ms_id, project, module, type)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    case_scene = VALUES(case_scene),
                    ms_id = VALUES(ms_id),
                    project = VALUES(project),
                    module = VALUES(module),
                    type = VALUES(type)
            ''', (case_name, case_scene, ms_id, project, module, type))
            self.connection.commit()
            logger.info(f"用例信息已保存/更新: {case_name}")
            return True
        except pymysql_err.OperationalError as e:
            logger.error(f"保存用例信息失败: {e}")
            return False
        finally:
            cursor.close()

    def clear_case_info_table(self) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM test_case_info")
            self.connection.commit()
            logger.info("用例信息表已清空")
            return True
        except pymysql_err.OperationalError as e:
            logger.error(f"清空用例信息表失败: {e}")
            return False
        finally:
            cursor.close()

    def batch_insert_case_info(self, case_list: List[Dict]) -> int:
        if not self.connection:
            return 0
        cursor = self.connection.cursor()
        success_count = 0
        try:
            for case_info in case_list:
                try:
                    cursor.execute('''
                        INSERT INTO test_case_info (case_name, case_scene, ms_id, project, module, type)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                            case_scene = VALUES(case_scene),
                            ms_id = VALUES(ms_id),
                            project = VALUES(project),
                            module = VALUES(module),
                            type = VALUES(type)
                    ''', (case_info.get('case_name'), case_info.get('case_scene'),
                          case_info.get('ms_id'), case_info.get('project'),
                          case_info.get('module'), case_info.get('type', 1)))
                    success_count += 1
                except pymysql_err.OperationalError as e:
                    logger.error(f"保存用例信息失败 {case_info.get('case_name')}: {e}")
            self.connection.commit()
            logger.info(f"批量保存用例信息完成，成功 {success_count}/{len(case_list)} 条")
            return success_count
        finally:
            cursor.close()

    def get_case_info_by_name(self, case_name: str) -> Optional[Dict]:
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM test_case_info WHERE case_name = %s", (case_name,))
            return cursor.fetchone()
        except pymysql_err.OperationalError as e:
            logger.error(f"查询用例信息失败: {e}")
            return None
        finally:
            cursor.close()

    def get_all_case_info(self) -> List[Dict]:
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM test_case_info ORDER BY project, module, case_name")
            return cursor.fetchall()
        except pymysql_err.OperationalError as e:
            logger.error(f"查询用例信息失败: {e}")
            return []
        finally:
            cursor.close()

    def get_active_version(self, version: str) -> Optional[Dict]:
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                SELECT version, version_info, backup_time, backup_user, created_at, updated_at
                FROM test_versions
                WHERE version = %s AND is_active = 1
            ''', (version,))
            result = cursor.fetchone()
            if result:
                logger.info(f"找到有效版本: {version}")
                return {
                    "version": result['version'],
                    "version_info": result['version_info'],
                    "backup_time": result['backup_time'],
                    "backup_user": result['backup_user'],
                    "created_at": result['created_at'],
                    "updated_at": result['updated_at']
                }
            return None
        except pymysql_err.OperationalError as e:
            logger.error(f"查询版本信息失败: {e}")
            return None
        finally:
            cursor.close()

    def insert_or_update_version(self, version: str, backup_user: str,
                               version_info: str = None) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            existing = self.get_active_version(version)
            if existing:
                cursor.execute('''
                    UPDATE test_versions
                    SET version_info = %s, backup_time = %s, backup_user = %s
                    WHERE version = %s AND is_active = 1
                ''', (version_info, datetime.now(), backup_user, version))
                logger.info(f"版本 {version} 已更新")
            else:
                cursor.execute('''
                    INSERT INTO test_versions
                    (version, version_info, backup_time, backup_user, is_active)
                    VALUES (%s, %s, %s, %s, 1)
                ''', (version, version_info, datetime.now(), backup_user))
                logger.info(f"版本 {version} 已创建")
            self.connection.commit()
            return True
        except pymysql_err.OperationalError as e:
            logger.error(f"保存版本信息失败: {e}")
            return False
        finally:
            cursor.close()

    def mark_version_deleted(self, version: str) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                UPDATE test_versions SET is_active = 0
                WHERE version = %s AND is_active = 1
            ''', (version,))
            self.connection.commit()
            logger.info(f"版本 {version} 已标记为删除")
            return True
        except pymysql_err.OperationalError as e:
            logger.error(f"标记版本删除失败: {e}")
            return False
        finally:
            cursor.close()

    def get_all_active_versions(self) -> List[Dict]:
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                SELECT version, version_info, backup_time, backup_user, created_at, updated_at
                FROM test_versions
                WHERE is_active = 1
                ORDER BY updated_at DESC
            ''')
            return cursor.fetchall()
        except pymysql_err.OperationalError as e:
            logger.error(f"查询版本列表失败: {e}")
            return []
        finally:
            cursor.close()

    def insert_execution_start(self, command: str, project: str = None,
                               module: str = None, case: str = None,
                               timeout_minutes: int = 30, version: str = None,
                               plan_id: int = None, plan_name: str = None) -> int:
        if not self.connection:
            return -1
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO test_execution
                (start_time, status, command, project, module, `case`, version, timeout_minutes, plan_id, plan_name)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (datetime.now(), 'running', command, project, module, case, version,
                  timeout_minutes, plan_id, plan_name))
            self.connection.commit()
            execution_id = cursor.lastrowid
            logger.info(f"执行记录已创建，ID: {execution_id}")
            return execution_id
        except pymysql_err.OperationalError as e:
            logger.error(f"插入执行记录失败: {e}")
            return -1
        finally:
            cursor.close()

    # ==================== 测试计划相关（MySQL） ====================

    def create_plan(self, plan_name: str, description: str = None,
                    creator: str = None) -> int:
        if not self.connection:
            return -1
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                INSERT INTO test_plan (plan_name, description, creator, is_active)
                VALUES (%s, %s, %s, 1)
            ''', (plan_name, description, creator))
            self.connection.commit()
            plan_id = cursor.lastrowid
            logger.info(f"测试计划已创建，ID: {plan_id}, 名称: {plan_name}")
            return plan_id
        except Exception as e:
            logger.error(f"创建测试计划失败: {e}")
            return -1
        finally:
            cursor.close()

    def get_all_plans(self) -> List[Dict]:
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                SELECT p.*,
                    (SELECT COUNT(*) FROM test_plan_case c WHERE c.plan_id = p.id) as case_count
                FROM test_plan p
                WHERE p.is_active = 1
                ORDER BY p.id DESC
            ''')
            return cursor.fetchall()
        except pymysql_err.OperationalError as e:
            logger.error(f"查询测试计划列表失败: {e}")
            return []
        finally:
            cursor.close()

    def get_plan_by_id(self, plan_id: int) -> Optional[Dict]:
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM test_plan WHERE id = %s AND is_active = 1", (plan_id,))
            return cursor.fetchone()
        except pymysql_err.OperationalError as e:
            logger.error(f"查询测试计划失败: {e}")
            return None
        finally:
            cursor.close()

    def get_plan_by_name(self, plan_name: str) -> Optional[Dict]:
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM test_plan WHERE plan_name = %s AND is_active = 1", (plan_name,))
            return cursor.fetchone()
        except pymysql_err.OperationalError as e:
            logger.error(f"查询测试计划失败: {e}")
            return None
        finally:
            cursor.close()

    def get_cases_by_plan(self, plan_id: int) -> List[str]:
        if not self.connection:
            return []
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT case_name FROM test_plan_case WHERE plan_id = %s", (plan_id,))
            return [row['case_name'] for row in cursor.fetchall()]
        except pymysql_err.OperationalError as e:
            logger.error(f"查询计划用例失败: {e}")
            return []
        finally:
            cursor.close()

    def update_plan_cases(self, plan_id: int, case_names: List[str]) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            cursor.execute("DELETE FROM test_plan_case WHERE plan_id = %s", (plan_id,))
            for case_name in case_names:
                cursor.execute("INSERT INTO test_plan_case (plan_id, case_name) VALUES (%s, %s)",
                               (plan_id, case_name))
            cursor.execute("UPDATE test_plan SET updated_at = %s WHERE id = %s", (datetime.now(), plan_id))
            self.connection.commit()
            logger.info(f"计划 {plan_id} 用例已更新，共 {len(case_names)} 条")
            return True
        except Exception as e:
            logger.error(f"更新计划用例失败: {e}")
            return False
        finally:
            cursor.close()

    def update_plan_desc(self, plan_id: int, description: str) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            cursor.execute("UPDATE test_plan SET description = %s, updated_at = %s WHERE id = %s",
                           (description, datetime.now(), plan_id))
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"更新计划描述失败: {e}")
            return False
        finally:
            cursor.close()

    def delete_plan(self, plan_id: int) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            # 真删除：先删关联用例，再删计划主记录
            cursor.execute("DELETE FROM test_plan_case WHERE plan_id = %s", (plan_id,))
            cursor.execute("DELETE FROM test_plan WHERE id = %s", (plan_id,))
            self.connection.commit()
            logger.info(f"测试计划已删除（物理删除），ID: {plan_id}")
            return True
        except Exception as e:
            logger.error(f"删除测试计划失败: {e}")
            return False
        finally:
            cursor.close()

    # ==================== 用例修复任务相关（MySQL） ====================

    def insert_fix_task(self, project: str, case_name: str, execution_id: int,
                        source_code: str) -> int:
        if not self.connection:
            return -1
        cursor = self.connection.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO fix_failed_case
                (project, case_name, execution_id, source_code, status, start_time)
                VALUES (%s, %s, %s, %s, '进行中', %s)
            ''', (project, case_name, execution_id, source_code, now))
            self.connection.commit()
            task_id = cursor.lastrowid
            logger.info(f"用例修复任务已创建，ID: {task_id}")
            return task_id
        except Exception as e:
            logger.error(f"创建用例修复任务失败: {e}")
            return -1
        finally:
            cursor.close()

    def update_fix_task_result(self, task_id: int, error_analysis: str,
                               fixed_code: str, status: str = '已完成') -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE fix_failed_case
                SET error_analysis = %s, fixed_code = %s, status = %s, end_time = %s
                WHERE id = %s
            ''', (error_analysis, fixed_code, status, now, task_id))
            self.connection.commit()
            logger.info(f"用例修复任务已更新，ID: {task_id}, 状态: {status}")
            return True
        except Exception as e:
            logger.error(f"更新用例修复任务失败: {e}")
            return False
        finally:
            cursor.close()

    def update_fix_task_status(self, task_id: int, status: str) -> bool:
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE fix_failed_case SET status = %s, end_time = %s WHERE id = %s
            ''', (status, now, task_id))
            self.connection.commit()
            logger.info(f"用例修复任务状态已更新，ID: {task_id}, 状态: {status}")
            return True
        except Exception as e:
            logger.error(f"更新用例修复任务状态失败: {e}")
            return False
        finally:
            cursor.close()

    def get_fix_task(self, task_id: int) -> Optional[Dict]:
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute("SELECT * FROM fix_failed_case WHERE id = %s", (task_id,))
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"查询用例修复任务失败: {e}")
            return None
        finally:
            cursor.close()

    def get_fix_task_by_case(self, project: str, case_name: str,
                             execution_id: int) -> Optional[Dict]:
        """根据项目、用例名称、执行ID查询最新一条修复任务"""
        if not self.connection:
            return None
        cursor = self.connection.cursor()
        try:
            cursor.execute('''
                SELECT * FROM fix_failed_case
                WHERE project = %s AND case_name = %s AND execution_id = %s
                ORDER BY id DESC LIMIT 1
            ''', (project, case_name, execution_id))
            return cursor.fetchone()
        except Exception as e:
            logger.error(f"查询用例修复任务失败: {e}")
            return None
        finally:
            cursor.close()

    def reset_fix_task(self, task_id: int) -> bool:
        """重置修复任务为进行中：清空结果、结束时间，更新开始时间"""
        if not self.connection:
            return False
        cursor = self.connection.cursor()
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                UPDATE fix_failed_case
                SET status = %s, error_analysis = NULL, fixed_code = NULL,
                    end_time = NULL, start_time = %s
                WHERE id = %s
            ''', ('进行中', now, task_id))
            self.connection.commit()
            logger.info(f"用例修复任务已重置，ID: {task_id}")
            return True
        except Exception as e:
            logger.error(f"重置用例修复任务失败: {e}")
            return False
        finally:
            cursor.close()


class TestResultDB:
    """测试结果数据库操作类（自动选择后端）"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.connection = None
        self._backend = None
        self._backend_type = config.get('backend', 'mysql')
        self._init_backend()

    def _init_backend(self):
        if self._backend_type == 'sqlite':
            db_path = self.config.get('sqlite_path', 'data/test_results.db')
            if not os.path.isabs(db_path):
                project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                db_path = os.path.join(project_root, db_path)
            self._backend = SQLiteDatabaseBackend(db_path)
        else:
            self._validate_mysql_config()
            self._backend = MySQLDatabaseBackend(self.config)

    def _validate_mysql_config(self):
        required_fields = ['host', 'port', 'user', 'database_name']
        for field in required_fields:
            if field not in self.config or not self.config[field]:
                raise DatabaseError(f"缺少必需的数据库配置字段: {field}")

    def connect(self) -> bool:
        result = self._backend.connect()
        if result:
            self.connection = self._backend.connection
        return result

    def close(self):
        self._backend.close()
        self.connection = None

    def create_tables(self) -> bool:
        return self._backend.create_tables()

    def create_plan_tables(self) -> bool:
        return self._backend.create_plan_tables()

    def update_execution_total_cases(self, execution_id: int, total_cases: int) -> bool:
        return self._backend.update_execution_total_cases(execution_id, total_cases)

    def update_execution_complete(self, execution_id: int, total_cases: int,
                                   passed_cases: int, status: str = 'completed') -> bool:
        return self._backend.update_execution_complete(execution_id, total_cases, passed_cases, status)

    def update_execution_timeout(self, execution_id: int) -> bool:
        return self._backend.update_execution_timeout(execution_id)

    def check_and_update_timeout_executions(self) -> int:
        return self._backend.check_and_update_timeout_executions()

    def insert_case_result(self, execution_id: int, case_name: str,
                          status: str, duration: float, log: str,
                          error_message: str = None, project: str = None) -> bool:
        return self._backend.insert_case_result(execution_id, case_name, status, duration, log, error_message, project)

    def batch_insert_case_results(self, execution_id: int, results: List[Dict], project: str = None) -> int:
        return self._backend.batch_insert_case_results(execution_id, results, project)

    def get_execution_by_id(self, execution_id: int) -> Optional[Dict]:
        return self._backend.get_execution_by_id(execution_id)

    def get_recent_executions(self, limit: int = 10) -> List[Dict]:
        return self._backend.get_recent_executions(limit)

    def get_case_results_by_execution(self, execution_id: int) -> List[Dict]:
        return self._backend.get_case_results_by_execution(execution_id)

    def get_case_results_summary(self, execution_id: int) -> List[Dict]:
        """列过滤版：不取 log 大字段"""
        return self._backend.get_case_results_summary(execution_id)

    def get_case_info_map(self, case_names: List[str]) -> Dict[str, Dict]:
        """批量查用例信息，消除 N+1"""
        return self._backend.get_case_info_map(case_names)

    def get_failed_cases(self, limit: int = 50) -> List[Dict]:
        return self._backend.get_failed_cases(limit)

    def get_statistics(self) -> Optional[Dict]:
        return self._backend.get_statistics()

    def insert_or_update_case_info(self, case_name: str, case_scene: str = None,
                                  ms_id: str = None, project: str = None,
                                  module: str = None, type: int = 1) -> bool:
        return self._backend.insert_or_update_case_info(case_name, case_scene, ms_id, project, module, type)

    def clear_case_info_table(self) -> bool:
        return self._backend.clear_case_info_table()

    def batch_insert_case_info(self, case_list: List[Dict]) -> int:
        return self._backend.batch_insert_case_info(case_list)

    def get_case_info_by_name(self, case_name: str) -> Optional[Dict]:
        return self._backend.get_case_info_by_name(case_name)

    def get_all_case_info(self) -> List[Dict]:
        return self._backend.get_all_case_info()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def get_active_version(self, version: str) -> Optional[Dict]:
        return self._backend.get_active_version(version)

    def insert_or_update_version(self, version: str, backup_user: str,
                               version_info: str = None) -> bool:
        return self._backend.insert_or_update_version(version, backup_user, version_info)

    def mark_version_deleted(self, version: str) -> bool:
        return self._backend.mark_version_deleted(version)

    def get_all_active_versions(self) -> List[Dict]:
        return self._backend.get_all_active_versions()

    def insert_execution_start(self, command: str, project: str = None,
                               module: str = None, case: str = None,
                               timeout_minutes: int = 30, version: str = None,
                               plan_id: int = None, plan_name: str = None) -> int:
        return self._backend.insert_execution_start(command, project, module, case,
                                                    timeout_minutes, version, plan_id, plan_name)

    # ==================== 测试计划相关（门面转发） ====================

    def create_plan(self, plan_name: str, description: str = None, creator: str = None) -> int:
        return self._backend.create_plan(plan_name, description, creator)

    def get_all_plans(self) -> List[Dict]:
        return self._backend.get_all_plans()

    def get_plan_by_id(self, plan_id: int) -> Optional[Dict]:
        return self._backend.get_plan_by_id(plan_id)

    def get_plan_by_name(self, plan_name: str) -> Optional[Dict]:
        return self._backend.get_plan_by_name(plan_name)

    def get_cases_by_plan(self, plan_id: int) -> List[str]:
        return self._backend.get_cases_by_plan(plan_id)

    def update_plan_cases(self, plan_id: int, case_names: List[str]) -> bool:
        return self._backend.update_plan_cases(plan_id, case_names)

    def update_plan_desc(self, plan_id: int, description: str) -> bool:
        return self._backend.update_plan_desc(plan_id, description)

    def delete_plan(self, plan_id: int) -> bool:
        return self._backend.delete_plan(plan_id)

    # ==================== 用例修复任务相关（门面转发） ====================

    def insert_fix_task(self, project: str, case_name: str, execution_id: int,
                        source_code: str) -> int:
        return self._backend.insert_fix_task(project, case_name, execution_id, source_code)

    def update_fix_task_result(self, task_id: int, error_analysis: str,
                               fixed_code: str, status: str = '已完成') -> bool:
        return self._backend.update_fix_task_result(task_id, error_analysis, fixed_code, status)

    def update_fix_task_status(self, task_id: int, status: str) -> bool:
        return self._backend.update_fix_task_status(task_id, status)

    def get_fix_task(self, task_id: int) -> Optional[Dict]:
        return self._backend.get_fix_task(task_id)

    def get_fix_task_by_case(self, project: str, case_name: str,
                             execution_id: int) -> Optional[Dict]:
        return self._backend.get_fix_task_by_case(project, case_name, execution_id)

    def reset_fix_task(self, task_id: int) -> bool:
        return self._backend.reset_fix_task(task_id)


class CaseResultCollector:
    """测试用例结果收集器（pytest插件）"""

    def __init__(self, db_obj=None, execution_id=None):
        self.results = []
        self.db_obj = db_obj
        self.execution_id = execution_id
        self.total_cases = 0

    def _extract_case_name(self, nodeid):
        if not nodeid:
            return ""
        parts = nodeid.split('/')[-1]
        parts = parts.replace('.py', '')
        segments = parts.split('::')
        if len(segments) >= 3:
            method_name = segments[-1]
            if method_name.startswith('test_'):
                return method_name[5:]
            return method_name
        elif len(segments) == 2:
            method_name = segments[-1]
            if method_name.startswith('test_'):
                return method_name[5:]
            return method_name
        else:
            if parts.startswith('test_'):
                return parts[5:]
            return parts

    def pytest_collection_modifyitems(self, session, config, items):
        self.total_cases = len(items)
        if self.db_obj and self.execution_id:
            try:
                self.db_obj.update_execution_total_cases(self.execution_id, self.total_cases)
            except Exception as e:
                logger.error(f"更新总用例数失败: {e}")

    def pytest_runtest_logreport(self, report):
        if report.when != 'call':
            return
        case_name = self._extract_case_name(report.nodeid)
        status = report.outcome
        duration = report.duration
        error_message = None
        if status == "failed" and hasattr(report, 'longrepr'):
            error_message = str(report.longrepr)
        log = ""
        if hasattr(report, 'caplog'):
            if hasattr(report.caplog, 'text'):
                log = report.caplog.text
            elif isinstance(report.caplog, str):
                log = report.caplog
        elif hasattr(report, 'stdout'):
            log = report.stdout or ""
        self.results.append({
            "case_name": case_name,
            "status": status,
            "duration": duration,
            "log": log,
            "error_message": error_message
        })


def get_db_instance(config: Dict[str, Any]) -> TestResultDB:
    return TestResultDB(config)


def is_mysql_available() -> bool:
    return PYMYSQL_AVAILABLE


def is_database_available() -> bool:
    return True


def parse_junit_xml(xml_path: str) -> list:
    """解析 pytest --junit-xml 输出，返回用例结果列表。

    用于在 subprocess 模式下替代 CaseResultCollector 插件。
    返回 [{"case_name", "status", "duration", "log", "error_message"}]
    """
    import xml.etree.ElementTree as ET

    results = []
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as e:
        logger.error(f"解析 junit-xml 失败: {e}")
        return results

    for tc in root.iter("testcase"):
        nodeid = tc.get("name", "")
        # 取方法名（去掉 test_ 前缀，跟 CaseResultCollector._extract_case_name 保持一致）
        case_name = nodeid
        if case_name.startswith("test_"):
            case_name = case_name[5:]
        # 处理参数化用例：name 形如 "test_field_config_all_modules[物料档案]"
        if "[" in case_name:
            method = case_name.split("[", 1)[0]
            param = case_name.split("[", 1)[1].rstrip("]")
            if method.startswith("test_"):
                method = method[5:]
            case_name = f"{method}[{param}]"

        # 状态：有 failure/error 节点 → failed/error，否则 passed
        failure = tc.find("failure")
        error = tc.find("error")
        skipped = tc.find("skipped")
        if failure is not None:
            status = "failed"
            error_message = failure.get("message") or failure.text
        elif error is not None:
            status = "error"
            error_message = error.get("message") or error.text
        elif skipped is not None:
            status = "skipped"
            error_message = skipped.get("message")
        else:
            status = "passed"
            error_message = None

        try:
            duration = float(tc.get("time", "0"))
        except (ValueError, TypeError):
            duration = 0.0

        results.append({
            "case_name": case_name,
            "status": status,
            "duration": duration,
            "log": "",
            "error_message": (error_message or "")[:8000] or None,
        })

    return results
