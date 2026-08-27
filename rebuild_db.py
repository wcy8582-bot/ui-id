"""
强制重建数据库表脚本
删除旧表并重新创建新表结构
"""
from src.common.database import TestResultDB
from src.common.config_loader import config_loader

def main():
    print("=" * 50)
    print("强制重建数据库表")
    print("=" * 50)

    # 获取配置
    config = config_loader.get_config()
    db_config = config.get('database', {})

    db_config_dict = {
        'backend': db_config.get('backend', 'mysql'),
        'sqlite_path': db_config.get('sqlite_path', 'data/test_results.db'),
        'host': db_config.get('host', '127.0.0.1'),
        'port': int(db_config.get('port', 3306)),
        'user': db_config.get('user', 'root'),
        'password': db_config.get('password', ''),
        'database_name': db_config.get('database_name', 'uitest'),
        'charset': db_config.get('charset', 'utf8mb4')
    }

    print(f"\n数据库配置:")
    print(f"  后端: {db_config_dict['backend']}")
    if db_config_dict['backend'] == 'sqlite':
        print(f"  数据库文件: {db_config_dict['sqlite_path']}")
    else:
        print(f"  主机: {db_config_dict['host']}")
        print(f"  端口: {db_config_dict['port']}")
        print(f"  用户: {db_config_dict['user']}")
        print(f"  数据库: {db_config_dict['database_name']}")

    print("\n开始强制重建表结构...")

    # 当前数据库包含的全部表
    tables = [
        'test_execution   (执行记录，含 plan_id / plan_name)',
        'test_case_result (用例结果)',
        'test_case_info   (用例信息)',
        'test_versions    (版本信息)',
        'test_plan        (测试计划主表)',
        'test_plan_case   (计划-用例关联表)',
        'fix_failed_case  (用例修复任务)',
    ]

    db = TestResultDB(db_config_dict)
    if db.connect():
        try:
            print("删除旧表...")
            db._backend.drop_tables()
            print("旧表已删除")

            print("创建新表...")
            # create_tables 内部会先建测试计划相关表（test_plan / test_plan_case）
            # 并为 test_execution 补充 plan_id / plan_name 列
            db.create_tables()

            print("\n已重建以下表:")
            for t in tables:
                print(f"  - {t}")
            print("\n数据库表重建完成！")
        except Exception as e:
            print(f"\n重建表失败: {e}")
        finally:
            db.close()
    else:
        print("\n数据库连接失败")

if __name__ == '__main__':
    main()