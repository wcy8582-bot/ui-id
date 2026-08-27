import os
import subprocess
import tempfile
import click

from src.common.ai_layering import ai_layering
from src.common.ai_formatting import format_recorded_code
from src.common.config_loader import config_loader
from src.common.logger import logger
from src.common.file_utils import FileUtils


@click.command()
@click.option('--project', '-p', required=True, help='项目名')
@click.option('--module', '-m', required=True, help='模块名')
@click.option('--case', '-c', required=True, help='用例名')
@click.option('--url', '-u', default=None, help='被测网站地址（可选，不传则从配置文件获取）')
@click.option('--username', '-U', default=None, help='登录用户名（可选，不传则从配置文件获取）')
@click.option('--pwd', '-P', default=None, help='登录密码（可选，不传则从配置文件获取）')
@click.option('--browser', '-b', default='chromium', help='浏览器类型')
@click.option('--output', '-o', default=None, help='输出路径')
@click.option('--format', '-f', default='0', help='是否AI格式化代码，0-否，1-是')
@click.option('--layering', '-l', default='0', help='是否AI分层代码，0-否，1-是')
@click.option('--ms_id', '-ms', default='0', help='用例ms的id')
def record(project, module, case, url, username, pwd, browser, output, format, layering, ms_id):
    """统一录制功能入口
    
    Args:
        project: 项目名
        module: 模块名
        ms_id: 用例ms的id
        case: 用例名
        url: 被测网站地址（可选，不传则从配置文件获取）
        username: 登录用户名（可选，不传则从配置文件获取）
        pwd: 登录密码（可选，不传则从配置文件获取）
        browser: 浏览器类型
        output: 输出路径
        format: 是否AI格式化代码，0-否，1-是
        layering: 是否AI分层代码，0-否，1-是
    """
    try:
        # 初始化日志，设置任务类型和用例名
        logger.init_logger(task_type="record", case_name=case)
        
        logger.info(f"开始录制: 项目={project}, 模块={module}, 用例={case}, ms_id={ms_id}")
        
        # 初始化配置
        config = config_loader.get_config()
        
        # 确定使用的URL（如果没有传入则从配置文件获取）
        if url is None and project in config.get('project_login', {}):
            url = config['project_login'][project].get('login_url', 'https://www.baidu.com')
        elif url is None:
            url = 'https://www.baidu.com'
        
        # 自动创建目录结构
        base_dir = output if output else os.path.dirname(os.path.abspath(__file__))
        pages_dir = os.path.join(base_dir, 'src', 'pages', project, module)
        data_dir = os.path.join(base_dir, 'src', 'data', project, module)
        testcase_dir = os.path.join(base_dir, 'src', 'testcase', project, module)
        
        for dir_path in [pages_dir, data_dir, testcase_dir]:
            FileUtils.create_directory(dir_path)
        
        # 生成临时文件路径
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file_path = temp_file.name
        
        try:
            # 启动Playwright Codegen录制
            logger.info(f"启动Playwright Codegen，浏览器: {browser}，URL: {url}")

            # 构建 codegen 命令参数
            codegen_cmd = [
                'python', '-m', 'playwright', 'codegen',
                '--browser', browser,
                '--viewport-size', '1920,1080',
                '--output', temp_file_path,
                url
            ]

            # 如果配置了忽略 HTTPS 错误，则添加参数
            if config.get('browser', {}).get('ignore_https_errors', False):
                codegen_cmd.append('--ignore-https-errors')
                logger.info("已启用忽略 HTTPS 证书错误")

            result = subprocess.run(
                codegen_cmd,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                logger.error(f"录制失败: {result.stderr}")
                return
            
            # 读取录制的代码
            with open(temp_file_path, 'r', encoding='utf-8') as f:
                recorded_code = f.read()
            
            if not recorded_code:
                logger.error("录制代码为空")
                return
            
            logger.info("录制完成，录制完的代码:")
            logger.info(recorded_code)
            
            # 根据format参数决定是否使用AI格式化
            if format == '1':
                logger.info("开始AI代码格式化")
                try:
                    # 使用AI处理录制的代码
                    processed_code = format_recorded_code(recorded_code, project, module, case, ms_id)
                    
                    logger.info(f"代码格式化完成:")
                    logger.info(processed_code)

                    # 判断是否需要AI分层
                    if layering == '1':
                        logger.info("开始AI代码分层")
                        try:
                            # 调用AI分层方法
                            layering_result = ai_layering(processed_code, project, module, case, ms_id)
                            
                            if layering_result['success']:
                                # AI分层成功，生成三层文件
                                logger.info("AI分层成功，开始生成三层文件")
                                
                                # 生成文件名
                                test_file = os.path.join(testcase_dir, f'test_{case}.py')
                                page_file = os.path.join(pages_dir, f'page_{case}.py')
                                data_file = os.path.join(data_dir, f'data_{case}.py')
                                
                                # 写入文件
                                FileUtils.write_file(test_file, layering_result['test_case'])
                                FileUtils.write_file(page_file, layering_result['page'])
                                FileUtils.write_file(data_file, layering_result['data'])
                                
                                logger.info(f"三层文件生成完成：")
                                logger.info(f"- 测试用例文件: {test_file}")
                                logger.info(layering_result['test_case'])
                                logger.info(f"- 页面对象文件: {page_file}")
                                logger.info(layering_result['page'])
                                logger.info(f"- 数据文件: {data_file}")
                                logger.info(layering_result['data'])
                                
                                print(f"\n录制完成！生成的文件：")
                                print(f"- 测试用例文件: {test_file}")
                                print(f"- 页面对象文件: {page_file}")
                                print(f"- 数据文件: {data_file}")
                                print(f"\n执行命令示例：")
                                print(f"python run.py -p {project} -m {module} -c {case}")
                            else:
                                # AI分层失败，保存格式化后的代码到testcase目录
                                logger.warning(f"AI分层失败: {layering_result['error']}")
                                logger.info("保存格式化后的代码到testcase目录")
                                
                                test_file = os.path.join(testcase_dir, f'test_{case}.py')
                                FileUtils.write_file(test_file, processed_code)
                                
                                logger.info(f"格式化后的代码已保存: {test_file}")
                                print(f"\nAI分层失败，保存格式化后的代码：")
                                print(f"- 测试用例文件: {test_file}")
                                print(f"\n执行命令示例：")
                                print(f"python run.py -p {project} -m {module} -c {case}")
                        except Exception as e:
                            logger.error(f"AI分层过程发生异常: {str(e)}")
                            logger.info("保存格式化后的代码到testcase目录")
                            
                            test_file = os.path.join(testcase_dir, f'test_{case}.py')
                            FileUtils.write_file(test_file, processed_code)
                            
                            logger.info(f"格式化后的代码已保存: {test_file}")
                            print(f"\nAI分层过程发生异常，保存格式化后的代码：")
                            print(f"- 测试用例文件: {test_file}")
                            print(f"\n执行命令示例：")
                            print(f"python run.py -p {project} -m {module} -c {case}")
                    else:
                        # 不需要分层，直接保存格式化后的代码
                        logger.info("不需要AI分层，保存格式化后的代码")
                        test_file = os.path.join(testcase_dir, f'test_{case}.py')
                        FileUtils.write_file(test_file, processed_code)
                        
                        logger.info(f"格式化后的代码已保存: {test_file}")
                        print(f"\n录制完成！生成的文件：")
                        print(f"- 测试用例文件: {test_file}")
                        print(f"\n执行命令示例：")
                        print(f"python run.py -p {project} -m {module} -c {case}")
                        
                except Exception as e:
                    logger.error(f"AI代码格式化失败: {str(e)}")
                    logger.info("直接保存录制的代码到testcase目录")
                    
                    # 直接保存录制的代码到testcase目录
                    test_file = os.path.join(testcase_dir, f'test_{case}.py')
                    FileUtils.write_file(test_file, recorded_code)
                    
                    logger.info(f"录制的代码已保存: {test_file}")
                    print(f"\nAI代码格式化失败，直接保存录制的代码：")
                    print(f"- 测试用例文件: {test_file}")
                    print(f"\n执行命令示例：")
                    print(f"python run.py -p {project} -m {module} -c {case}")
            else:
                # format为0，直接保存录制的代码
                logger.info("直接保存录制的代码到testcase目录")
                test_file = os.path.join(testcase_dir, f'test_{case}.py')
                FileUtils.write_file(test_file, recorded_code)
                
                logger.info(f"录制的代码已保存: {test_file}")
                print(f"\n录制完成！生成的文件：")
                print(f"- 测试用例文件: {test_file}")
                print(f"\n执行命令示例：")
                print(f"python run.py -p {project} -m {module} -c {case}")
            
        finally:
            # 清理临时文件
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
    except Exception as e:
        logger.error(f"录制过程发生错误: {str(e)}")
        print(f"录制过程发生错误: {str(e)}")


if __name__ == '__main__':
    record()
