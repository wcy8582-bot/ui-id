import os
import sys
import time
import click
import pytest
from datetime import datetime
from src.common.config_loader import config_loader
from src.common.logger import logger
from src.common.file_utils import FileUtils
from src.common.database import TestResultDB, CaseResultCollector, is_mysql_available, parse_junit_xml
from src.common.webhook import WebhookClient
from src.common.version_control import get_current_version


def build_db_config_dict(config):
    """从全局配置构建数据库连接配置字典"""
    db_config = config.get('database', {})
    return {
        'backend': db_config.get('backend', 'mysql'),
        'sqlite_path': db_config.get('sqlite_path', 'data/test_results.db'),
        'host': db_config.get('host', 'localhost'),
        'port': int(db_config.get('port', 3306)),
        'user': db_config.get('user', 'root'),
        'password': db_config.get('password', ''),
        'database_name': db_config.get('database_name', 'test_results_db'),
        'charset': db_config.get('charset', 'utf8mb4'),
        'connect_timeout': db_config.get('connect_timeout', 30)
    }


def resolve_plan_test_files(config, plan_name):
    """根据测试计划名称解析出对应的 pytest 测试文件路径列表

    Args:
        config: 全局配置
        plan_name: 测试计划名称（唯一）

    Returns:
        tuple: (test_files: List[str], plan_id: int)
               解析失败返回 ([], None)
    """
    if not is_mysql_available():
        logger.error("数据库不可用，无法按测试计划执行")
        return [], None

    db = TestResultDB(build_db_config_dict(config))
    if not db.connect():
        logger.error("数据库连接失败，无法按测试计划执行")
        return [], None

    try:
        plan = db.get_plan_by_name(plan_name)
        if not plan:
            logger.error(f"未找到测试计划: {plan_name}")
            return [], None

        plan_id = plan['id']
        case_names = db.get_cases_by_plan(plan_id)
        if not case_names:
            logger.warning(f"测试计划 {plan_name} 下没有绑定任何用例")
            return [], plan_id

        testcase_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'testcase')
        test_files = []
        for case_name in case_names:
            case_info = db.get_case_info_by_name(case_name)
            if not case_info:
                logger.warning(f"用例 {case_name} 在用例信息表中不存在，已跳过")
                continue
            project = case_info.get('project')
            module = case_info.get('module')
            if not project or not module:
                logger.warning(f"用例 {case_name} 缺少 project/module 信息，已跳过")
                continue
            file_path = os.path.join(testcase_base, project, module, f'test_{case_name}.py')
            if not os.path.exists(file_path):
                logger.warning(f"用例文件不存在，已跳过: {file_path}")
                continue
            test_files.append(file_path)

        logger.info(f"测试计划 {plan_name} 共解析出 {len(test_files)}/{len(case_names)} 个可执行用例文件")
        return test_files, plan_id
    finally:
        db.close()


def send_test_report_email(execution_time: float, result: int, test_output: str = ""):
    """发送测试报告邮件

    Args:
        execution_time: 执行耗时（秒）
        result: 执行结果（0成功，非0失败）
        test_output: 测试输出内容
    """
    try:
        from playwright.sync_api import sync_playwright

        # 邮件配置
        mail_url = "https://mail.supcon.com/coremail/"
        username = "zhangyang10@supcon.com"
        password = "Supcon@1304"
        recipient = "zhangyang10@supcon.com"

        # 构建邮件内容
        result_text = "成功" if result == 0 else "失败"

        # 截取输出的最后部分（避免内容过长）
        max_output_length = 8000
        if len(test_output) > max_output_length:
            test_output = "..." + test_output[-max_output_length:]

        email_body = f"""自动化测试执行完成

执行时间: {execution_time:.2f}秒
执行结果: {result_text}

测试详情:
{test_output}

---
本邮件由自动化测试框架发送
"""

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            # 登录邮箱
            page.goto(mail_url)
            page.get_by_role("textbox", name="用户名").click()
            page.get_by_role("textbox", name="用户名").fill(username)
            page.get_by_role("textbox", name="密 码").click()
            page.get_by_role("textbox", name="密 码").fill(password)
            page.get_by_role("button", name="登录").click()
            page.wait_for_timeout(3000)

            # 点击写信
            page.get_by_role("button", name=" 写 信").click()
            page.wait_for_timeout(1000)

            # 填写收件人
            page.get_by_role("list").filter(has_text=",").click()
            page.get_by_role("listitem").filter(has_text=",").get_by_role("textbox").fill(recipient)
            page.wait_for_timeout(500)

            # 填写邮件内容
            page.locator("iframe").first.content_frame.locator("body").click()
            page.locator("iframe").first.content_frame.locator("body").fill(email_body)
            page.wait_for_timeout(500)

            # 发送邮件
            page.get_by_text("发 送").click()
            page.wait_for_timeout(1000)

            # 确认发送
            if page.get_by_role("button", name="确定").is_visible():
                page.get_by_role("button", name="确定").click()

            page.wait_for_timeout(2000)
            browser.close()

        logger.info("测试报告邮件已发送")
        print("\n测试报告邮件已发送")

    except Exception as e:
        logger.error(f"发送邮件失败: {str(e)}")
        print(f"\n发送邮件失败: {str(e)}")


@click.command()
@click.option('--project', '-p', default=None, help='项目名')
@click.option('--url', '-u', default=None, help='项目登录URL')
@click.option('--username', '-user', default=None, help='登录用户名')
@click.option('--pwd', '-pwd', default=None, help='登录密码')
@click.option('--module', '-m', default=None, help='模块名')
@click.option('--case', '-c', default=None, help='用例名')
@click.option('--browser', '-b', default=None, help='浏览器类型')
@click.option('--headless', '-hl', default=None, type=bool, help='无头模式开关')
@click.option('--retry', '-r', default=None, type=int, help='重试次数')
@click.option('--parallel', '-pl', default=None, type=int, help='并行数')
@click.option('--clean', is_flag=True, help='执行前清理历史日志/截图/报告')
@click.option('--report-type', default='allure', type=click.Choice(['allure', 'html']), help='报告类型')
@click.option('--email', '-e', is_flag=True, help='执行完成后发送邮件通知')
@click.option('--wh', '-w', default=1, type=int, help='是否推送webhook（0=不推送，1=推送）')
@click.option('--plan_name', '-pn', default=None, help='测试计划名称，传入时忽略-m/-c，按计划执行')
def run(project, url, username, pwd, module, case, browser, headless, retry, parallel, clean, report_type, email, wh, plan_name):
    """统一测试执行入口

    Args:
        project: 项目名
        url: 项目登录URL（可选，不传则从配置文件获取）
        username: 登录用户名（可选，不传则从配置文件获取）
        pwd: 登录密码（可选，不传则从配置文件获取）
        module: 模块名
        case: 用例名
        browser: 浏览器类型
        headless: 无头模式开关
        retry: 重试次数
        parallel: 并行数
        clean: 执行前清理历史日志/截图/报告
        report_type: 报告类型
        email: 执行完成后发送邮件通知
        wh: 是否推送webhook（0=不推送，1=推送）
    """
    try:
        # 初始化配置
        config = config_loader.get_config()

        # 更新配置
        updates = {}
        if project:
            updates['execution_scope'] = {'target_project': project}
        if module:
            updates['execution_scope'] = {'target_modules': [module]}
        if browser:
            updates['browser'] = {'browser_type': browser}
        if headless is not None:
            updates['browser'] = {'headless': headless}
        if retry is not None:
            updates['execution'] = {'max_retry_count': retry}
        if parallel is not None:
            updates['execution'] = {'parallel_workers': parallel}

        # 处理登录信息
        # 1. 确定使用的项目
        target_project = project or config['execution_scope'].get('target_project', '*')
        # 2. 检查是否需要更新登录信息
        if url is not None or (username is not None and pwd is not None):
            # 获取现有配置作为基础
            existing_login = config.get('project_login', {}).get(target_project, {})
            login_info = {
                'login_url': url or existing_login.get('login_url', ''),
                'username': username or existing_login.get('username', ''),
                'password': pwd or existing_login.get('password', '')
            }
            # 更新配置
            if 'project_login' not in updates:
                updates['project_login'] = {}
            updates['project_login'][target_project] = login_info

        if updates:
            config_loader.update_config(updates)

        # 获取更新后的配置
        config = config_loader.get_config()

        # 执行前置操作
        if clean:
            logger.info("清理历史文件")
            expired_days = config['global']['expired_days']
            FileUtils.clean_expired_files(config['paths']['logs_root_dir'], expired_days)
            FileUtils.clean_expired_files(config['paths']['screenshots_root_dir'], expired_days)
            FileUtils.clean_expired_files(config['paths']['reports_root_dir'], expired_days)

        # 初始化日志
        logger.init_logger(
            config['paths']['logs_root_dir'],
            config['global']['enable_debug_log'],
            task_type="run",
            case_name=case if case else "all"
        )

        logger.info("开始执行测试")
        
        # 获取并记录当前版本号
        current_version = get_current_version()
        logger.info(f"当前测试版本: {current_version}")

        # 构建Pytest参数
        pytest_args = []

        # 测试计划相关变量（默认非计划模式）
        plan_id = None

        if plan_name:
            # ========== 测试计划模式：忽略 -m / -c，直接按计划解析用例文件 ==========
            logger.info(f"测试计划模式，计划名称: {plan_name}")
            plan_test_files, plan_id = resolve_plan_test_files(config, plan_name)
            if plan_id is None:
                logger.error(f"测试计划 {plan_name} 无效，终止执行")
                print(f"错误: 测试计划 {plan_name} 不存在或数据库不可用")
                exit(1)
            if not plan_test_files:
                logger.error(f"测试计划 {plan_name} 下没有可执行的用例，终止执行")
                print(f"错误: 测试计划 {plan_name} 下没有可执行的用例")
                exit(1)
            pytest_args.extend(plan_test_files)
        else:
            # ========== 普通模式：按项目-模块-用例过滤 ==========
            # 构建测试路径
            test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'testcase')

            # 获取目标项目（优先使用参数，否则从配置文件获取）
            target_project_for_path = project
            if not target_project_for_path:
                default_project = config['execution_scope'].get('target_project', '')
                if default_project and default_project != '*':
                    target_project_for_path = default_project

            if target_project_for_path:
                test_path = os.path.join(test_path, target_project_for_path)
                if module:
                    test_path = os.path.join(test_path, module)
                    if case:
                        test_path = os.path.join(test_path, f'test_{case}.py')
            elif module:
                # 如果没有指定项目但指定了模块，查找所有项目下是否有该模块
                import glob
                module_pattern = os.path.join(test_path, '*', module)
                matching_paths = glob.glob(module_pattern)

                if matching_paths:
                    # 如果找到多个，使用第一个（按字母顺序排序）
                    matching_paths.sort()
                    test_path = matching_paths[0]
                    logger.info(f"在项目 {os.path.basename(os.path.dirname(test_path))} 中找到模块 {module}")
                    if case:
                        test_path = os.path.join(test_path, f'test_{case}.py')
                else:
                    # 如果没找到，尝试直接在testcase下查找
                    test_path = os.path.join(test_path, module)
                    if case:
                        test_path = os.path.join(test_path, f'test_{case}.py')

            pytest_args.append(test_path)

        # 使用单线程运行
        logger.info("使用单线程运行测试，避免Playwright Sync API在asyncio循环中的错误")

        # 禁用xdist插件，确保测试依次执行
        pytest_args.extend(['-p', 'no:xdist'])

        # 按照文件顺序执行测试
        pytest_args.extend(['--tb=short'])

        # 失败重试
        if config['execution']['max_retry_count'] > 0:
            pytest_args.extend(['--tb=short', '--timeout=3600'])
            # 注意：这里需要pytest-rerunfailures插件
            # pytest_args.extend(['--reruns', str(config['execution']['max_retry_count'])])

        # 失败立即停止
        if config['execution']['fail_fast']:
            pytest_args.append('-x')

        # 用例过滤
        if config['execution']['case_filter']:
            pytest_args.extend(['-k', config['execution']['case_filter']])

        # 报告配置
        timestamp = time.strftime('%Y%m%d_%H%M%S')
        if report_type == 'allure':
            allure_dir = os.path.join(config['paths']['reports_root_dir'], f"allure_report_{timestamp}")
            pytest_args.extend(['--alluredir', allure_dir])
        elif report_type == 'html':
            html_report = os.path.join(config['paths']['reports_root_dir'], f"report_{timestamp}.html")
            pytest_args.extend(['--html', html_report])

        logger.info(f"Pytest执行参数: {pytest_args}")

        # 初始化数据库（从配置文件获取配置）
        db_obj = None
        case_collector = None
        execution_id = None
        if is_mysql_available():
            db_config = config.get('database', {})
            db_config_dict = {
                'backend': db_config.get('backend', 'mysql'),
                'sqlite_path': db_config.get('sqlite_path', 'data/test_results.db'),
                'host': db_config.get('host', 'localhost'),
                'port': db_config.get('port', 3306),
                'user': db_config.get('user', 'root'),
                'password': db_config.get('password', ''),
                'database_name': db_config.get('database_name', 'test_results_db'),
                'charset': db_config.get('charset', 'utf8mb4'),
                'connect_timeout': db_config.get('connect_timeout', 30)
            }

            db_obj = TestResultDB(db_config_dict)
            if db_obj.connect():
                db_obj.create_tables()

                # 检查并更新超时的执行记录
                db_obj.check_and_update_timeout_executions()

                # 构建命令字符串
                command_parts = ["python", "run.py"]
                if plan_name:
                    command_parts.extend(["--plan_name", plan_name])
                else:
                    if project:
                        command_parts.extend(["-p", project])
                    if module:
                        command_parts.extend(["-m", module])
                    if case:
                        command_parts.extend(["-c", case])
                command_str = " ".join(command_parts)

                # 获取当前版本号
                version = get_current_version()

                # 插入执行记录（状态为 running）
                # 计划模式下 project/module/case 留空，改用 plan_id/plan_name 标识
                execution_id = db_obj.insert_execution_start(
                    command=command_str,
                    project=None if plan_name else project,
                    module=None if plan_name else module,
                    case=None if plan_name else case,
                    timeout_minutes=30,
                    version=version,
                    plan_id=plan_id,
                    plan_name=plan_name
                )

                if execution_id != -1:
                    case_collector = CaseResultCollector(db_obj=db_obj, execution_id=execution_id)
                    sys.stdout.write(f"EXECUTION_ID:{execution_id}\n")
                    sys.stdout.flush()
                    logger.info(f"执行记录已创建，ID: {execution_id}")
                else:
                    db_obj.close()
                    db_obj = None
            else:
                db_obj = None
                logger.warning("数据库连接失败，将不保存测试结果")

        if execution_id is None or execution_id == -1:
            sys.stdout.write("EXECUTION_ID:-1\n")
            sys.stdout.flush()

        # 设置环境变量传递项目名称
        if plan_name:
            # 计划模式：取第一个用例文件所属的项目作为环境项目
            # （一期约束：建议计划内用例同项目；跨项目登录切换留待后续）
            plan_project_for_env = None
            if 'plan_test_files' in dir() and plan_test_files:
                # 路径结构: .../src/testcase/{project}/{module}/test_xxx.py
                first_file = plan_test_files[0]
                plan_project_for_env = os.path.basename(
                    os.path.dirname(os.path.dirname(first_file))
                )
            if plan_project_for_env:
                os.environ['PROJECT_NAME'] = plan_project_for_env
                logger.info(f"计划模式环境项目设置为: {plan_project_for_env}")
        else:
            # 普通模式：如果project不传，从配置文件获取默认项目名称
            target_project_for_env = project or config['execution_scope'].get('target_project', 'default')
            if target_project_for_env and target_project_for_env != '*':
                os.environ['PROJECT_NAME'] = target_project_for_env

        # 记录开始时间
        start_time = time.time()

        # 执行测试
        if case_collector:
            # 使用 subprocess 执行 pytest，避免 playwright sync API 与
            # pytest.main() 主进程 asyncio loop 死锁。
            # 通过 --junit-xml 输出再解析来收集用例结果，替代 CaseResultCollector 插件。
            import subprocess
            import tempfile

            junit_xml_path = os.path.join(
                tempfile.gettempdir(),
                f"pytest_result_{int(time.time())}.xml"
            )
            pytest_args_with_xml = pytest_args + [f"--junit-xml={junit_xml_path}"]
            pytest_cmd = ["python", "-m", "pytest"] + pytest_args_with_xml
            logger.info(f"Pytest命令(subprocess): {' '.join(pytest_cmd)}")

            try:
                process = subprocess.Popen(
                    pytest_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1,
                )

                output_lines = []
                for line in process.stdout:
                    output_lines.append(line)
                    print(line, end='')

                process.wait()
                test_output = ''.join(output_lines)
                result = process.returncode
            except Exception as e:
                logger.error(f"subprocess 执行 pytest 失败: {e}")
                test_output = f"subprocess 执行失败: {e}\n"
                result = 1

            # 解析 junit-xml 重建用例结果到 case_collector.results
            if os.path.exists(junit_xml_path):
                try:
                    parsed_results = parse_junit_xml(junit_xml_path)
                    case_collector.results = parsed_results
                    logger.info(f"已从 junit-xml 解析 {len(parsed_results)} 条用例结果")
                except Exception as e:
                    logger.error(f"解析 junit-xml 失败: {e}")
                finally:
                    try:
                        os.remove(junit_xml_path)
                    except OSError:
                        pass
            else:
                logger.warning("junit-xml 文件不存在，无法收集用例级结果")
        elif email:
            # 如果需要发送邮件，使用subprocess捕获输出
            try:
                import subprocess

                # 构建pytest命令
                pytest_cmd = ["python", "-m", "pytest"] + pytest_args
                logger.info(f"Pytest命令: {' '.join(pytest_cmd)}")

                # 执行pytest并捕获输出
                process = subprocess.Popen(
                    pytest_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )

                # 实时获取输出
                output_lines = []
                for line in process.stdout:
                    output_lines.append(line)
                    print(line, end='')  # 同时打印到控制台

                process.wait()
                test_output = ''.join(output_lines)
                result = process.returncode

            except Exception as e:
                logger.error(f"捕获测试输出失败: {str(e)}")
                test_output = f"捕获测试输出失败: {str(e)}\n"
                result = 1
        else:
            # 原有的pytest执行方式
            result = pytest.main(pytest_args)
            test_output = ""

        end_time = time.time()

        # 更新执行记录（执行完成）
        if db_obj and execution_id:
            try:
                # 统计结果
                total_cases = len(case_collector.results) if case_collector else 0
                passed_cases = sum(1 for r in case_collector.results if r['status'] == 'passed') if case_collector else 0

                # 根据 pytest 结果确定状态
                final_status = 'completed' if result == 0 else 'failed'

                # 更新执行记录
                db_obj.update_execution_complete(
                    execution_id=execution_id,
                    total_cases=total_cases,
                    passed_cases=passed_cases,
                    status=final_status
                )

                # 保存每条用例结果
                if case_collector and case_collector.results:
                    saved_count = 0
                    for case_result in case_collector.results:
                        if db_obj.insert_case_result(
                            execution_id=execution_id,
                            case_name=case_result['case_name'],
                            status=case_result['status'],
                            duration=case_result['duration'],
                            log=case_result['log'],
                            error_message=case_result['error_message'],
                            project=project
                        ):
                            saved_count += 1
                    logger.info(f"已保存 {saved_count}/{total_cases} 条用例结果")
            except Exception as e:
                logger.error(f"保存测试结果到数据库失败: {str(e)}")
            finally:
                db_obj.close()

        # 清理环境变量
        if 'PROJECT_NAME' in os.environ:
            del os.environ['PROJECT_NAME']

        # 生成Allure报告
        if report_type == 'allure':
            try:
                import subprocess
                import shutil

                # 检查allure命令是否可用
                if shutil.which('allure') is None:
                    raise Exception("Allure命令行工具未找到，请确保已安装并添加到系统PATH中")

                allure_report_dir = os.path.join(config['paths']['reports_root_dir'], f"allure_report_{timestamp}_html")

                # 打印调试信息
                logger.info(f"Allure命令: allure generate {allure_dir} -o {allure_report_dir} --clean")
                logger.info(f"Allure命令路径: {shutil.which('allure')}")
                logger.info(f"Allure数据目录存在: {os.path.exists(allure_dir)}")
                logger.info(f"Allure报告目录父目录存在: {os.path.exists(os.path.dirname(allure_report_dir))}")

                # 确保报告目录父目录存在
                os.makedirs(os.path.dirname(allure_report_dir), exist_ok=True)

                # 使用绝对路径执行命令
                allure_cmd = shutil.which('allure')
                if allure_cmd:
                    subprocess.run([allure_cmd, 'generate', allure_dir, '-o', allure_report_dir, '--clean'], check=True)
                else:
                    raise Exception("Allure命令行工具未找到，请确保已安装并添加到系统PATH中")
                logger.info(f"Allure报告已生成: {allure_report_dir}")
                print(f"\nAllure报告已生成: {allure_report_dir}")
                print(f"\n打开报告指令: allure serve \"{allure_dir}\"")
            except Exception as e:
                logger.error(f"生成Allure报告失败: {str(e)}")
                print(f"\n生成Allure报告失败: {str(e)}")
                print("提示: 请确保已安装Allure命令行工具并添加到系统PATH中")
                print("或者使用HTML报告代替: python run.py -p <项目> -m <模块> --report-type html")

        # 输出执行概览
        execution_time = end_time - start_time
        logger.info(f"测试执行完成，耗时: {execution_time:.2f}秒")
        logger.info(f"执行结果: {'成功' if result == 0 else '失败'}")

        print(f"\n执行概览:")
        print(f"- 耗时: {execution_time:.2f}秒")
        print(f"- 结果: {'成功' if result == 0 else '失败'}")

        # 输出数据库保存状态
        if execution_id:
            print(f"- 执行记录ID: {execution_id}")
            print(f"- 数据库保存: 已保存")
        elif not is_mysql_available():
            print(f"- 数据库保存: pymysql 未安装")
        else:
            print(f"- 数据库保存: 失败")

        # 发送邮件通知
        if email:
            # 发送邮件
            send_test_report_email(execution_time, result, test_output)

        # 发送 webhook 通知
        if wh == 1:
            try:
                webhook_client = WebhookClient()
                status = 'completed' if result == 0 else 'failed'
                total_cases = len(case_collector.results) if case_collector else 0
                passed_cases = sum(1 for r in case_collector.results if r['status'] == 'passed') if case_collector else 0
                
                webhook_client.send_execution_result(
                    project=project,
                    module=module,
                    case=case,
                    status=status,
                    total_cases=total_cases,
                    passed_cases=passed_cases,
                    start_time=datetime.fromtimestamp(start_time),
                    end_time=datetime.fromtimestamp(end_time)
                )
            except Exception as e:
                logger.error(f"发送 webhook 失败: {str(e)}")
                print(f"\n发送 webhook 失败: {str(e)}")

        # 返回系统退出码
        exit(result)

    except Exception as e:
        logger.error(f"执行过程发生错误: {str(e)}")
        print(f"执行过程发生错误: {str(e)}")
        exit(1)


if __name__ == '__main__':
    run()
