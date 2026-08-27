"""
用例信息扫描脚本
用于扫描所有测试用例文件，提取用例信息并插入到数据库中
这是更新用例表的唯一方法
"""
import os
import re
from src.common.database import TestResultDB
from src.common.config_loader import config_loader


def parse_case_info(file_path):
    """
    解析单个测试用例文件，提取用例信息

    Args:
        file_path: 测试用例文件路径

    Returns:
        dict: 用例信息字典，包含 case_name, case_scene, ms_id, project, module
    """
    # 从路径中提取项目、模块和用例名
    # 路径格式: src/testcase/{project}/{module}/test_{case_name}.py
    relative_path = os.path.relpath(file_path, os.path.join(os.path.dirname(__file__), 'src', 'testcase'))
    parts = relative_path.replace('\\', '/').split('/')

    if len(parts) >= 3:
        project = parts[0]
        module = parts[1]
        filename = parts[-1]
        # 从文件名提取用例名（去掉 test_ 前缀和 .py 后缀）
        case_name = filename.replace('test_', '').replace('.py', '')
    else:
        project = None
        module = None
        case_name = None

    # 读取文件内容，提取注释中的用例场景和 ms_id
    case_scene = None
    ms_id = None
    case_type = 1  # 默认基础用例

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 首先尝试从类级别的 docstring 提取 ms_id 和 type
        class_docstring_match = re.search(r'class\s+\w+.*?"""(.*?)"""', content, re.DOTALL)
        if class_docstring_match:
            class_docstring = class_docstring_match.group(1)
            # 从类 docstring 提取 ms_id
            ms_id_match = re.search(r'用例ms的id\s*[：:]\s*(\d+)', class_docstring)
            if ms_id_match:
                ms_id = ms_id_match.group(1)

            # 从类 docstring 提取 type
            type_match = re.search(r'type\s*[：:]\s*(.+?)[\n\r]', class_docstring)
            if type_match:
                type_value = type_match.group(1).strip()
                if type_value == '场景用例':
                    case_type = 2

        # 从方法级别的 docstring 提取用例场景
        # 匹配 test_ 开头的方法的 docstring
        method_pattern = r'def\s+(test_\w+)\s*\([^)]*\):\s*(?:\s*#.*)?\s*(f?"""(.*?)""")'
        method_matches = re.findall(method_pattern, content, re.DOTALL)

        for method_name, _, method_docstring in method_matches:
            # 提取第一行作为用例场景（去掉 f-string 标记）
            lines = method_docstring.strip().split('\n')
            for line in lines:
                line = line.strip()
                # 跳过空行和特殊标记行
                if not line:
                    continue
                if line.startswith('用例名') or line.startswith('用例ms') or line.startswith('项目名'):
                    continue
                if line.startswith('Args:') or line.startswith('Returns:') or line.startswith('Note:'):
                    break
                # 找到用例场景
                case_scene = line
                break

            # 如果类 docstring 中没有 ms_id，尝试从方法 docstring 提取
            if not ms_id:
                ms_id_match = re.search(r'用例ms的id\s*[：:]\s*(\d+)', method_docstring)
                if ms_id_match:
                    ms_id = ms_id_match.group(1)

            # 只处理第一个 test_ 方法
            break

    except Exception as e:
        print(f"读取文件 {file_path} 失败: {e}")

    return {
        'case_name': case_name,
        'case_scene': case_scene,
        'ms_id': ms_id,
        'project': project,
        'module': module,
        'type': case_type
    }


def scan_test_cases(base_path):
    """
    扫描目录下所有测试用例文件

    Args:
        base_path: 测试用例目录路径

    Returns:
        list: 用例信息列表
    """
    case_list = []

    for root, dirs, files in os.walk(base_path):
        for filename in files:
            if filename.startswith('test_') and filename.endswith('.py'):
                file_path = os.path.join(root, filename)
                case_info = parse_case_info(file_path)
                if case_info['case_name']:
                    case_list.append(case_info)
                    print(f"已扫描: {case_info['project']}/{case_info['module']}/{case_info['case_name']}")

    return case_list


def main():
    print("=" * 60)
    print("用例信息扫描脚本")
    print("=" * 60)

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

    # 扫描用例
    testcase_path = os.path.join(os.path.dirname(__file__), 'src', 'testcase')
    print(f"\n扫描目录: {testcase_path}")
    print("\n正在扫描测试用例...")

    case_list = scan_test_cases(testcase_path)
    print(f"\n扫描完成，共找到 {len(case_list)} 个用例")

    if not case_list:
        print("未找到任何测试用例")
        return

    # 显示扫描结果
    print("\n扫描结果:")
    for i, case in enumerate(case_list, 1):
        print(f"{i}. {case['project']}/{case['module']}/{case['case_name']}")
        print(f"   场景: {case['case_scene'] or '未设置'}")
        print(f"   MS ID: {case['ms_id'] or '未设置'}")
        print(f"   类型: {'场景用例' if case.get('type') == 2 else '基础用例'}")

    # # 确认插入
    # confirm = input("\n确认将这些用例信息插入数据库？(y/n): ").strip().lower()
    # if confirm != 'y' and confirm != 'yes':
    #     print("操作已取消")
    #     return

    # 连接数据库并插入
    print("\n连接数据库...")
    db = TestResultDB(db_config_dict)
    if not db.connect():
        print("数据库连接失败")
        return

    print("清空用例信息表...")
    if not db.clear_case_info_table():
        print("清空用例信息表失败")
        db.close()
        return

    print("插入用例信息...")
    success_count = db.batch_insert_case_info(case_list)
    db.close()

    print(f"\n" + "=" * 60)
    print(f"成功插入/更新 {success_count} 条用例信息")
    print("=" * 60)


if __name__ == '__main__':
    main()
