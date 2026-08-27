"""
测试用例管理网页应用
提供用例列表查看、筛选、执行等功能
支持代码热更新（修改代码后自动生效，无需重启服务）
"""
import os
import sys
import subprocess
import threading
import time
from datetime import datetime
from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory, after_this_request

# 热更新相关导入
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

# 初始导入（服务启动时使用）
from src.common.database import TestResultDB
from src.common.config_loader import config_loader
from src.common.module_definition_loader import module_def_loader
from src.common.logger import logger
from src.common.version_control import (
    get_current_version,
    backup_version,
    create_new_version_with_info,
    switch_version,
    delete_version,
    get_version_info,
    get_all_versions,
    check_version_exists
)

app = Flask(__name__)

# 全局数据库连接配置
db_config = None

# 热更新相关全局变量
_reload_required = False
_last_reload_time = None
_watchdog_observer = None
_hot_reload_enabled = True

# 模块重新加载缓存
_module_reload_cache = {}


class HotReloadHandler(FileSystemEventHandler):
    """
    文件系统事件处理器，用于检测代码变化
    """
    
    def __init__(self):
        self.last_modified = {}
        
    def on_modified(self, event):
        """
        当文件被修改时触发
        """
        global _reload_required, _last_reload_time
        
        if not _hot_reload_enabled:
            return
            
        if event.is_directory:
            return
            
        # 只关注 Python 文件
        if not event.src_path.endswith('.py'):
            return
            
        # 忽略 .pyc 文件和 __pycache__ 目录
        if '.pyc' in event.src_path or '__pycache__' in event.src_path:
            return
            
        # 检查是否是最近刚修改的（防止重复触发）
        current_time = time.time()
        if event.src_path in self.last_modified:
            if current_time - self.last_modified[event.src_path] < 1:
                return
        self.last_modified[event.src_path] = current_time
        
        _reload_required = True
        _last_reload_time = datetime.now()
        
        # 打印日志
        relative_path = os.path.relpath(event.src_path, os.path.dirname(__file__))
        logger.info(f"[{_last_reload_time.strftime('%H:%M:%S')}] 检测到文件变化: {relative_path}，标记需要重新加载")


def start_file_watcher():
    """
    启动文件监控器
    """
    global _watchdog_observer
    
    if not WATCHDOG_AVAILABLE:
        logger.warning("watchdog 未安装，热更新功能不可用")
        return
        
    if not _hot_reload_enabled:
        logger.info("热更新功能已禁用")
        return
        
    try:
        # 监控 src 目录
        src_dir = os.path.join(os.path.dirname(__file__), 'src')
        
        if not os.path.exists(src_dir):
            logger.warning(f"监控目录不存在: {src_dir}")
            return
            
        event_handler = HotReloadHandler()
        _watchdog_observer = Observer()
        _watchdog_observer.schedule(event_handler, src_dir, recursive=True)
        _watchdog_observer.start()
        
        logger.info(f"热更新监控器已启动，监控目录: {src_dir}")
        
    except Exception as e:
        logger.error(f"启动文件监控器失败: {e}")


def stop_file_watcher():
    """
    停止文件监控器
    """
    global _watchdog_observer
    
    if _watchdog_observer:
        _watchdog_observer.stop()
        _watchdog_observer.join()
        _watchdog_observer = None
        logger.info("热更新监控器已停止")


def reload_modules():
    """
    重新加载所有相关模块
    """
    global _reload_required, _last_reload_time, config_loader, module_def_loader, TestResultDB, logger
    
    if not _reload_required:
        return False
        
    # 先打印到控制台（因为 logger 可能会被重新加载）
    print("=" * 60)
    print("开始重新加载模块...")
    current_time = datetime.now().strftime('%H:%M:%S')
    print(f"[{current_time}] 触发模块重新加载")
    
    try:
        # 重新加载配置加载器
        if 'src.common.config_loader' in sys.modules:
            del sys.modules['src.common.config_loader']
            
        # 重新加载模块定义加载器
        if 'src.common.module_definition_loader' in sys.modules:
            del sys.modules['src.common.module_definition_loader']
            
        # 重新加载数据库模块
        if 'src.common.database' in sys.modules:
            del sys.modules['src.common.database']
            
        # 重新加载日志模块
        if 'src.common.logger' in sys.modules:
            del sys.modules['src.common.logger']
            
        # 重新加载版本控制模块
        if 'src.common.version_control' in sys.modules:
            del sys.modules['src.common.version_control']
            
        # 重新导入模块
        from src.common.config_loader import config_loader
        from src.common.module_definition_loader import module_def_loader
        from src.common.database import TestResultDB
        from src.common.logger import logger
        
        # 重新初始化配置
        config_loader.reload_config()
        module_def_loader.reload_module_def()
        
        _reload_required = False
        _last_reload_time = datetime.now()
        
        # 使用新加载的 logger 记录日志
        logger.info("=" * 60)
        logger.info(f"模块重新加载完成，时间: {_last_reload_time.strftime('%H:%M:%S')}")
        logger.info("=" * 60)
        
        print(f"[{_last_reload_time.strftime('%H:%M:%S')}] 模块重新加载完成")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        # 打印到控制台和日志（如果 logger 可用）
        error_msg = f"模块重新加载失败: {e}"
        print(f"错误: {error_msg}")
        
        try:
            import traceback
            logger.error(error_msg)
            logger.error(traceback.format_exc())
        except:
            # logger 可能还没重新导入成功
            import traceback
            traceback.print_exc()
            
        return False


@app.before_request
def check_reload():
    """
    在每个请求前检查是否需要重新加载模块
    """
    global _reload_required
    
    if _reload_required and _hot_reload_enabled:
        reload_modules()


def init_db():
    """初始化数据库连接"""
    global db_config
    config = config_loader.get_config()
    db_config = config.get('database', {})

    # 确保测试计划相关表存在（独立于历史表结构，非破坏性）
    try:
        db = get_db_instance()
        if db.connect():
            db.create_plan_tables()
            db.close()
    except Exception as e:
        logger.error(f"初始化测试计划表失败: {e}")


def get_db_instance():
    """获取数据库实例"""
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
    return TestResultDB(db_config_dict)


@app.route('/')
def index():
    """用例列表页面"""
    return redirect(url_for('case_list'))


@app.route('/cases')
def case_list():
    """用例列表页面"""
    # 查询用例列表
    db = get_db_instance()
    if db.connect():
        all_cases = db.get_all_case_info()
        db.close()
    else:
        all_cases = []

    # 按项目→模块分组用例
    grouped_cases = {}
    for case in all_cases:
        project = case.get('project', '')
        module = case.get('module', '')
        if project not in grouped_cases:
            grouped_cases[project] = {}
        if module not in grouped_cases[project]:
            grouped_cases[project][module] = []
        grouped_cases[project][module].append(case)

    # 获取所有项目和模块（用于展示）
    all_projects = sorted(grouped_cases.keys())

    # 构建项目和模块的中文名映射
    project_names = {}
    module_names = {}
    for p in all_projects:
        project_names[p] = module_def_loader.get_project_name_cn(p)
        for m in grouped_cases[p].keys():
            module_names[m] = module_def_loader.get_module_name_cn(m)

    # 准备模板数据
    grouped_cases_json = []
    for project in all_projects:
        modules_list = []
        for module in sorted(grouped_cases[project].keys()):
            modules_list.append({
                'name': module,
                'name_cn': module_names.get(module, module),
                'count': len(grouped_cases[project][module])
            })
        grouped_cases_json.append({
            'name': project,
            'name_cn': project_names.get(project, project),
            'modules': modules_list
        })
    
    # 获取当前版本
    current_version = get_current_version()

    return render_template('case_list.html',
                           all_cases=all_cases,
                           grouped_cases_json=grouped_cases_json,
                           all_projects=all_projects,
                           project_names=project_names,
                           module_names=module_names,
                           current_version=current_version)


@app.route('/executions')
def execution_list():
    """执行记录列表页面"""
    db = get_db_instance()
    executions = []
    case_names = {}  # 用例名称到中文场景的映射
    
    if db.connect():
        # 先检查并更新超时记录
        db.check_and_update_timeout_executions()
        executions = db.get_recent_executions(limit=50)
        
        # 获取所有用例的中文名称
        all_cases = db.get_all_case_info()
        for case in all_cases:
            case_name = case.get('case_name', '')
            case_scene = case.get('case_scene', '')
            if case_name and case_scene:
                case_names[case_name] = case_scene
        
        db.close()

    # 构建项目和模块的中文名称映射
    project_names = {}
    module_names = {}
    
    # 收集所有项目和模块
    all_projects = set()
    all_modules = set()
    for exec in executions:
        if exec.get('project'):
            all_projects.add(exec['project'])
        if exec.get('module'):
            all_modules.add(exec['module'])
    
    # 获取中文名称
    for project in all_projects:
        project_names[project] = module_def_loader.get_project_name_cn(project)
    
    for module in all_modules:
        module_names[module] = module_def_loader.get_module_name_cn(module)

    return render_template(
        'execution_list.html', 
        executions=executions,
        project_names=project_names,
        module_names=module_names,
        case_names=case_names
    )


@app.route('/report/<int:execution_id>')
def report_page(execution_id):
    """测试报告页面"""
    db = get_db_instance()
    if not db.connect():
        return redirect('/executions')
    
    execution = db.get_execution_by_id(execution_id)
    if not execution:
        db.close()
        return redirect('/executions')
    
    # 列过滤：不取 log 大字段（日志走 /get_case_log 按需单条获取）
    cases = db.get_case_results_summary(execution_id)

    # 一次 IN 查询取回全部用例信息，替代逐条查询（消除 N+1）
    info_map = db.get_case_info_map([c['case_name'] for c in cases])
    for case in cases:
        case_info = info_map.get(case['case_name'])
        if case_info:
            case['case_scene'] = case_info.get('case_scene', '')
            case['project'] = case_info.get('project', '')
            case['module'] = case_info.get('module', '')
        else:
            case['case_scene'] = ''
            case['project'] = ''
            case['module'] = ''
    
    db.close()
    
    # 统计信息
    total = len(cases)
    passed = sum(1 for r in cases if r['status'] == 'passed')
    failed = sum(1 for r in cases if r['status'] == 'failed')
    pass_rate = round(passed / total * 100, 2) if total > 0 else 0
    
    # 计算耗时
    duration_str = ''
    import datetime
    if isinstance(execution['start_time'], datetime.datetime) and execution['end_time']:
        if isinstance(execution['end_time'], datetime.datetime):
            duration = execution['end_time'] - execution['start_time']
            duration_str = round(duration.total_seconds(), 2)
        else:
            try:
                end_str = str(execution['end_time'])
                end_time = None
                for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S']:
                    try:
                        end_time = datetime.datetime.strptime(end_str, fmt)
                        break
                    except ValueError:
                        continue
                if end_time:
                    duration = end_time - execution['start_time']
                    duration_str = round(duration.total_seconds(), 2)
                else:
                    duration_str = '-'
            except:
                duration_str = '-'
    
    # 查找截图和视频
    config = config_loader.get_config()
    screenshots_root = os.path.join(os.path.dirname(__file__), config['paths']['screenshots_root_dir'])
    videos_root = os.path.join(os.path.dirname(__file__), config['paths']['videos_root_dir'])
    
    # 获取执行时间戳，用于查找目录
    execution_ts = ''
    if isinstance(execution['start_time'], datetime.datetime):
        execution_ts = execution['start_time'].strftime('%Y%m%d_%H%M%S')
    else:
        try:
            ts_str = str(execution['start_time'])
            for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S']:
                try:
                    ts = datetime.datetime.strptime(ts_str, fmt)
                    execution_ts = ts.strftime('%Y%m%d_%H%M%S')
                    break
                except ValueError:
                    continue
            if not execution_ts:
                logger.warning(f'无法解析start_time: {ts_str}')
        except Exception as e:
            logger.warning(f'解析start_time异常: {e}')
    
    screenshots = {}
    videos = {}
    
    import glob
    import fnmatch
    logger.info(f'=== 开始查找截图和视频 ===')
    logger.info(f'screenshots_root: {screenshots_root}')
    logger.info(f'videos_root: {videos_root}')
    logger.info(f'execution_ts: {execution_ts}')
    
    # 查找截图目录
    if execution_ts:
        # 首先查找匹配的截图目录
        search_pattern = os.path.join(screenshots_root, execution_ts)
        screenshot_dirs = glob.glob(search_pattern + '*')
        logger.info(f'找到的时间戳匹配的截图目录: {screenshot_dirs}')
        
        if screenshot_dirs:
            # 使用第一个匹配的目录
            screenshot_dir = sorted(screenshot_dirs, key=os.path.getmtime, reverse=True)[0]
            logger.info(f'使用的截图根目录: {screenshot_dir}')
            
            # 截图的结构是：screenshot_dir/{project}/{module}/{case_name}
            # 需要递归查找所有包含case_name的目录
            
            for case in cases:
                case_name = case['case_name']
                logger.info(f'查找case: {case_name}')
                
                # 递归查找
                for root, dirs, files in os.walk(screenshot_dir):
                    # 检查当前目录是否包含case_name
                    if fnmatch.fnmatch(os.path.basename(root), '*' + case_name + '*'):
                        # 这是case目录
                        img_files = []
                        for ext in ['*.png', '*.jpg', '*.jpeg']:
                            full_paths = glob.glob(os.path.join(root, ext))
                            # 转换为相对于screenshots_root的路径
                            for full_path in full_paths:
                                rel_path = os.path.relpath(full_path, screenshots_root)
                                # 将 Windows 反斜杠转换为正斜杠
                                rel_path = rel_path.replace(os.sep, '/')
                                img_files.append(rel_path)
                        if img_files:
                            screenshots[case_name] = sorted(img_files, key=lambda x: os.path.getmtime(os.path.join(screenshots_root, x)), reverse=True)
                            logger.info(f'screenshots[{case_name}] = {screenshots[case_name]}')
                            break  # 找到后就不再查找了
        else:
            # 如果没有找到时间戳匹配的，尝试查找所有可能的目录
            logger.info(f'没有找到时间戳匹配的目录，尝试查找所有可能目录')
            
            all_screenshot_dirs = [d for d in os.listdir(screenshots_root) if os.path.isdir(os.path.join(screenshots_root, d))]
            for possible_dir_name in sorted(all_screenshot_dirs, key=lambda x: os.path.getmtime(os.path.join(screenshots_root, x)), reverse=True):
                possible_dir = os.path.join(screenshots_root, possible_dir_name)
                
                for case in cases:
                    if case['case_name'] not in screenshots:
                        case_name = case['case_name']
                        
                        # 递归查找
                        for root, dirs, files in os.walk(possible_dir):
                            if fnmatch.fnmatch(os.path.basename(root), '*' + case_name + '*'):
                                img_files = []
                                for ext in ['*.png', '*.jpg', '*.jpeg']:
                                    full_paths = glob.glob(os.path.join(root, ext))
                                    for full_path in full_paths:
                                        rel_path = os.path.relpath(full_path, screenshots_root)
                                        rel_path = rel_path.replace(os.sep, '/')
                                        img_files.append(rel_path)
                                if img_files:
                                    screenshots[case_name] = sorted(img_files, key=lambda x: os.path.getmtime(os.path.join(screenshots_root, x)), reverse=True)
                                    logger.info(f'找到case {case_name} 的截图在 {possible_dir}')
                                    break
    
    # 查找视频目录
    if execution_ts:
        # 查找视频目录
        video_search_pattern = os.path.join(videos_root, execution_ts)
        video_dirs = glob.glob(video_search_pattern + '*')
        logger.info(f'匹配到的视频目录: {video_dirs}')
        
        if video_dirs:
            video_dir = sorted(video_dirs, key=os.path.getmtime, reverse=True)[0]
            logger.info(f'使用的视频根目录: {video_dir}')
            
            # 视频结构是：video_dir/{case_name}
            for case in cases:
                case_name = case['case_name']
                # 查找case_name子目录
                case_video_pattern = os.path.join(video_dir, '*' + case_name + '*')
                case_video_dirs = glob.glob(case_video_pattern)
                
                if case_video_dirs:
                    case_video_dir = case_video_dirs[0]
                    # 获取所有视频
                    video_files = []
                    for ext in ['*.webm', '*.mp4', '*.mkv']:
                        full_paths = glob.glob(os.path.join(case_video_dir, ext))
                        for full_path in full_paths:
                            rel_path = os.path.relpath(full_path, videos_root)
                            rel_path = rel_path.replace(os.sep, '/')
                            video_files.append(rel_path)
                    if video_files:
                        videos[case_name] = sorted(video_files, key=lambda x: os.path.getmtime(os.path.join(videos_root, x)), reverse=True)
                        logger.info(f'videos[{case_name}] = {videos[case_name]}')
        else:
            # 没有找到时间戳匹配的，尝试查找所有可能
            logger.info(f'没有找到时间戳匹配的视频目录，尝试查找所有可能')
            
            all_video_dirs = [d for d in os.listdir(videos_root) if os.path.isdir(os.path.join(videos_root, d))]
            for possible_dir_name in sorted(all_video_dirs, key=lambda x: os.path.getmtime(os.path.join(videos_root, x)), reverse=True):
                possible_dir = os.path.join(videos_root, possible_dir_name)
                
                for case in cases:
                    if case['case_name'] not in videos:
                        case_name = case['case_name']
                        
                        case_video_pattern = os.path.join(possible_dir, '*' + case_name + '*')
                        case_video_dirs = glob.glob(case_video_pattern)
                        
                        if case_video_dirs:
                            case_video_dir = case_video_dirs[0]
                            video_files = []
                            for ext in ['*.webm', '*.mp4', '*.mkv']:
                                full_paths = glob.glob(os.path.join(case_video_dir, ext))
                                for full_path in full_paths:
                                    rel_path = os.path.relpath(full_path, videos_root)
                                    rel_path = rel_path.replace(os.sep, '/')
                                    video_files.append(rel_path)
                            if video_files:
                                videos[case_name] = sorted(video_files, key=lambda x: os.path.getmtime(os.path.join(videos_root, x)), reverse=True)
                                logger.info(f'找到case {case_name} 的视频在 {possible_dir}')
    
    logger.info(f'最终screenshots: {screenshots}')
    logger.info(f'最终videos: {videos}')
    
    # 环境信息（计划模式下 execution.project 可能为空，需容错）
    env_url = ''
    exec_project = execution.get('project')
    if exec_project and 'project_login' in config and exec_project in config['project_login']:
        env_url = config['project_login'][exec_project].get('login_url', '')
    
    return render_template('report.html',
                         execution=execution,
                         cases=cases,
                         total=total,
                         passed=passed,
                         failed=failed,
                         pass_rate=pass_rate,
                         duration_str=duration_str,
                         screenshots=screenshots,
                         videos=videos,
                         env_url=env_url,
                         module_def_loader=module_def_loader,
                         enumerate=enumerate)


@app.route('/screenshot/<path:filepath>')
def serve_screenshot(filepath):
    """提供截图文件访问"""
    try:
        import urllib.parse
        decoded_path = urllib.parse.unquote(filepath)
        logger.info(f'请求访问截图: {decoded_path}')
        
        config = config_loader.get_config()
        screenshots_root = os.path.join(os.path.dirname(__file__), config['paths']['screenshots_root_dir'])
        
        # 拼接完整路径
        full_path = os.path.join(screenshots_root, decoded_path)
        logger.info(f'full_path: {full_path}')
        
        # 安全检查
        full_path = os.path.abspath(full_path)
        real_screenshots_root = os.path.abspath(screenshots_root)
        
        if not full_path.startswith(real_screenshots_root):
            logger.error('路径不在安全范围内')
            return '', 404
        
        if os.path.exists(full_path):
            logger.info(f'文件存在，提供访问: {os.path.dirname(full_path)}, {os.path.basename(full_path)}')
            return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path))
        
        logger.error('文件不存在')
        return '', 404
    except Exception as e:
        logger.error(f'提供截图失败: {str(e)}')
        import traceback
        logger.error(traceback.format_exc())
        return '', 500


@app.route('/video/<path:filepath>')
def serve_video(filepath):
    """提供视频文件访问"""
    try:
        import urllib.parse
        decoded_path = urllib.parse.unquote(filepath)
        logger.info(f'请求访问视频: {decoded_path}')
        
        config = config_loader.get_config()
        videos_root = os.path.join(os.path.dirname(__file__), config['paths']['videos_root_dir'])
        
        # 拼接完整路径
        full_path = os.path.join(videos_root, decoded_path)
        logger.info(f'full_path: {full_path}')
        
        # 安全检查
        full_path = os.path.abspath(full_path)
        real_videos_root = os.path.abspath(videos_root)
        
        if not full_path.startswith(real_videos_root):
            logger.error('路径不在安全范围内')
            return '', 404
        
        if os.path.exists(full_path):
            logger.info(f'文件存在，提供访问: {os.path.dirname(full_path)}, {os.path.basename(full_path)}')
            return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path))
        
        logger.error('文件不存在')
        return '', 404
    except Exception as e:
        logger.error(f'提供视频失败: {str(e)}')
        import traceback
        logger.error(traceback.format_exc())
        return '', 500


@app.route('/update_cases', methods=['POST'])
def update_cases():
    """更新用例信息（执行 scan_case_info.py）"""
    try:
        # 在后台执行扫描脚本
        script_path = os.path.join(os.path.dirname(__file__), 'scan_case_info.py')
        subprocess.Popen(['python', script_path], cwd=os.path.dirname(__file__))
        return jsonify({'success': True, 'message': '用例更新已启动，请稍等片刻后刷新页面'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'执行失败: {str(e)}'})


@app.route('/execute_case', methods=['POST'])
def execute_case():
    """执行单条用例"""
    case_name = request.json.get('case_name')
    project = request.json.get('project')
    module = request.json.get('module')

    if not case_name or not project:
        return jsonify({'success': False, 'message': '缺少必要参数'})

    def run_test():
        """后台执行测试"""
        cmd = ['python', 'run.py', '-p', project]
        if module:
            cmd.extend(['-m', module])
        cmd.extend(['-c', case_name])
        subprocess.Popen(cmd, cwd=os.path.dirname(__file__))

    # 在后台线程中执行
    threading.Thread(target=run_test, daemon=True).start()
    return jsonify({'success': True, 'message': f'用例 {case_name} 执行已启动'})


@app.route('/execute_batch', methods=['POST'])
def execute_batch():
    """批量执行用例"""
    project = request.json.get('project')
    module = request.json.get('module', '')

    if not project:
        return jsonify({'success': False, 'message': '项目不能为空'})

    def run_test():
        """后台执行测试"""
        cmd = ['python', 'run.py', '-p', project]
        if module:
            cmd.extend(['-m', module])
        subprocess.Popen(cmd, cwd=os.path.dirname(__file__))

    # 在后台线程中执行
    threading.Thread(target=run_test, daemon=True).start()
    return jsonify({'success': True, 'message': f'批量执行已启动: {project}/{module or "所有模块"}'})


@app.route('/get_case_results/<int:execution_id>')
def get_case_results(execution_id):
    """获取执行记录的用例结果"""
    db = get_db_instance()
    if db.connect():
        results = db.get_case_results_by_execution(execution_id)
        db.close()
        return jsonify({'success': True, 'results': results})
    else:
        return jsonify({'success': False, 'message': '数据库连接失败'})


@app.route('/get_case_log/<int:execution_id>/<string:case_name>')
def get_case_log(execution_id, case_name):
    """获取指定用例的日志"""
    db = get_db_instance()
    if db.connect():
        results = db.get_case_results_by_execution(execution_id)
        db.close()
        # 找到对应的用例日志
        for result in results:
            if result['case_name'] == case_name:
                return jsonify({'success': True, 'log': result.get('log', '无日志')})
        return jsonify({'success': False, 'message': '未找到用例日志'})
    else:
        return jsonify({'success': False, 'message': '数据库连接失败'})


@app.route('/get_projects')
def get_projects():
    """获取所有项目列表"""
    db = get_db_instance()
    if db.connect():
        cases = db.get_all_case_info()
        db.close()
        projects = sorted(set(c.get('project') for c in cases if c.get('project')))
        return jsonify({'success': True, 'projects': projects})
    else:
        return jsonify({'success': False, 'projects': []})


@app.route('/get_modules/<string:project>')
def get_modules(project):
    """获取指定项目的模块列表"""
    db = get_db_instance()
    if db.connect():
        cases = db.get_all_case_info()
        db.close()
        modules = sorted(set(c.get('module') for c in cases if c.get('project') == project))
        return jsonify({'success': True, 'modules': modules})
    else:
        return jsonify({'success': False, 'modules': []})


@app.route('/update_project', methods=['POST'])
def update_project():
    """从git更新项目接口"""
    try:
        # 获取参数
        params = request.json or {}
        branch = params.get('branch', 'main')
        
        # 构建命令
        cmd = ['git', 'pull', 'origin', branch]
        
        def run_update():
            """后台执行更新"""
            result = subprocess.run(cmd, cwd=os.path.dirname(__file__), capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f'项目更新失败: {result.stderr}')
            else:
                logger.info(f'项目更新成功: {result.stdout}')
        
        # 在后台线程中执行
        threading.Thread(target=run_update, daemon=True).start()
        
        return jsonify({
            'success': True, 
            'message': f'项目更新已启动，正在拉取 {branch} 分支',
            'command': ' '.join(cmd)
        })
        
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'更新失败: {str(e)}'
        })


@app.route('/execute_test', methods=['POST'])
def execute_test():
    """执行测试接口，接收run.py的所有参数"""
    try:
        # 获取所有参数
        params = request.json or {}
        
        # 构建命令
        cmd = ['python', 'run.py']
        
        # 添加参数
        if params.get('project'):
            cmd.extend(['-p', params['project']])
        if params.get('url'):
            cmd.extend(['-u', params['url']])
        if params.get('username'):
            cmd.extend(['-user', params['username']])
        if params.get('pwd'):
            cmd.extend(['-pwd', params['pwd']])
        if params.get('module'):
            cmd.extend(['-m', params['module']])
        if params.get('case'):
            cmd.extend(['-c', params['case']])
        if params.get('browser'):
            cmd.extend(['-b', params['browser']])
        if 'headless' in params and params['headless'] is not None:
            cmd.extend(['--headless'] if params['headless'] else [])
        if params.get('retry') is not None:
            cmd.extend(['-r', str(params['retry'])])
        if params.get('parallel') is not None:
            cmd.extend(['-pl', str(params['parallel'])])
        if params.get('clean'):
            cmd.append('--clean')
        if params.get('report_type'):
            cmd.extend(['--report-type', params['report_type']])
        if params.get('email'):
            cmd.append('-e')
        if params.get('wh') is not None:
            cmd.extend(['-w', str(params['wh'])])
        
        command_str = ' '.join(cmd)
        execution_id = -1

        process = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(__file__),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        deadline = time.time() + 30
        while time.time() < deadline:
            line = process.stdout.readline()
            if not line:
                break
            line = line.strip()
            if line.startswith('EXECUTION_ID:'):
                try:
                    execution_id = int(line.split(':')[1])
                except ValueError:
                    pass
                break

        def consume_output():
            for _ in process.stdout:
                pass
            process.wait()

        threading.Thread(target=consume_output, daemon=True).start()

        response_data = {
            'success': True,
            'message': '测试执行已启动',
            'command': command_str
        }

        if execution_id != -1:
            response_data['execution_id'] = execution_id
        else:
            response_data['warning'] = '无法创建执行记录，可能是数据库连接失败'

        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f'执行测试失败: {str(e)}')
        return jsonify({
            'success': False, 
            'message': f'执行失败: {str(e)}'
        })


@app.route('/get_execution_status/<int:execution_id>', methods=['GET'])
def get_execution_status(execution_id):
    """测试状态查询API"""
    try:
        db = get_db_instance()
        if db.connect():
            execution = db.get_execution_by_id(execution_id)
            db.close()
            
            if execution:
                return jsonify({
                    'success': True,
                    'execution': execution
                })
            else:
                return jsonify({
                    'success': False,
                    'message': f'未找到执行ID为 {execution_id} 的记录'
                })
        else:
            return jsonify({
                'success': False,
                'message': '数据库连接失败'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        })


@app.route('/get_test_results/<int:execution_id>', methods=['GET'])
def get_test_results(execution_id):
    """测试结果获取API"""
    try:
        db = get_db_instance()
        if db.connect():
            # 获取执行信息
            execution = db.get_execution_by_id(execution_id)
            if not execution:
                db.close()
                return jsonify({
                    'success': False,
                    'message': f'未找到执行ID为 {execution_id} 的记录'
                })
            
            # 获取用例结果
            case_results = db.get_case_results_by_execution(execution_id)
            db.close()
            
            return jsonify({
                'success': True,
                'execution': execution,
                'case_results': case_results,
                'statistics': {
                    'total_cases': len(case_results),
                    'passed_cases': sum(1 for r in case_results if r['status'] == 'passed'),
                    'failed_cases': sum(1 for r in case_results if r['status'] == 'failed')
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': '数据库连接失败'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询失败: {str(e)}'
        })


@app.route('/download_report/<string:report_type>/<int:execution_id>', methods=['GET'])
def download_report(report_type, execution_id):
    """报告下载API"""
    try:
        # 验证报告类型
        if report_type not in ['allure', 'html']:
            return jsonify({
                'success': False,
                'message': '不支持的报告类型，仅支持 allure 和 html'
            })
        
        db = get_db_instance()
        if db.connect():
            # 获取执行信息
            execution = db.get_execution_by_id(execution_id)
            db.close()
            
            if not execution:
                return jsonify({
                    'success': False,
                    'message': f'未找到执行ID为 {execution_id} 的记录'
                })
            
            # 构建报告路径
            config = config_loader.get_config()
            reports_dir = os.path.join(os.path.dirname(__file__), config['paths']['reports_root_dir'])
            
            if report_type == 'allure':
                # 查找Allure报告目录
                import glob
                allure_dirs = glob.glob(os.path.join(reports_dir, f'allure_report_{execution_id}_*_html'))
                if not allure_dirs:
                    return jsonify({
                        'success': False,
                        'message': f'未找到执行ID为 {execution_id} 的Allure报告'
                    })
                
                # 返回最新的Allure报告
                report_path = sorted(allure_dirs, key=os.path.getmtime, reverse=True)[0]
                
                # 压缩报告目录
                import zipfile
                import tempfile
                import shutil
                
                temp_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
                temp_zip.close()
                
                with zipfile.ZipFile(temp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(report_path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, report_path)
                            zipf.write(file_path, arcname)
                
                # 返回压缩文件
                response = send_from_directory(
                    os.path.dirname(temp_zip.name),
                    os.path.basename(temp_zip.name),
                    as_attachment=True,
                    attachment_filename=f'allure_report_{execution_id}.zip'
                )
                
                # 清理临时文件
                @after_this_request
                def cleanup(response):
                    try:
                        os.unlink(temp_zip.name)
                    except Exception as e:
                        logger.error(f'清理临时文件失败: {str(e)}')
                    return response
                
                return response
            
            elif report_type == 'html':
                # 查找HTML报告文件
                import glob
                html_files = glob.glob(os.path.join(reports_dir, f'report_*_{execution_id}.html'))
                if not html_files:
                    return jsonify({
                        'success': False,
                        'message': f'未找到执行ID为 {execution_id} 的HTML报告'
                    })
                
                # 返回最新的HTML报告
                report_path = sorted(html_files, key=os.path.getmtime, reverse=True)[0]
                
                return send_from_directory(
                    os.path.dirname(report_path),
                    os.path.basename(report_path),
                    as_attachment=True,
                    attachment_filename=f'report_{execution_id}.html'
                )
        else:
            return jsonify({
                'success': False,
                'message': '数据库连接失败'
            })
    except Exception as e:
        logger.error(f'下载报告失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'下载失败: {str(e)}'
        })


# ==================== 热更新相关API ====================

@app.route('/hot_reload/status', methods=['GET'])
def hot_reload_status():
    """
    获取热更新状态
    """
    return jsonify({
        'success': True,
        'enabled': _hot_reload_enabled,
        'watchdog_available': WATCHDOG_AVAILABLE,
        'reload_required': _reload_required,
        'last_reload_time': _last_reload_time.strftime('%Y-%m-%d %H:%M:%S') if _last_reload_time else None,
        'monitoring': _watchdog_observer is not None and _watchdog_observer.is_alive()
    })


@app.route('/hot_reload/toggle', methods=['POST'])
def hot_reload_toggle():
    """
    切换热更新功能的启用/禁用状态
    """
    global _hot_reload_enabled
    
    _hot_reload_enabled = not _hot_reload_enabled
    
    if _hot_reload_enabled:
        # 重新启动监控器
        start_file_watcher()
        return jsonify({
            'success': True,
            'enabled': True,
            'message': '热更新功能已启用'
        })
    else:
        # 停止监控器
        stop_file_watcher()
        return jsonify({
            'success': True,
            'enabled': False,
            'message': '热更新功能已禁用'
        })


@app.route('/hot_reload/trigger', methods=['POST'])
def hot_reload_trigger():
    """
    手动触发模块重新加载
    """
    global _reload_required
    
    _reload_required = True
    
    # 立即执行重新加载
    result = reload_modules()
    
    return jsonify({
        'success': result,
        'message': '模块重新加载已触发' if result else '模块重新加载失败'
    })


@app.route('/hot_reload/info', methods=['GET'])
def hot_reload_info():
    """
    获取热更新相关的详细信息
    """
    return jsonify({
        'success': True,
        'description': '代码热更新功能',
        'features': [
            '自动检测 src 目录下的 Python 文件变化',
            '文件修改后在下一次请求时自动重新加载模块',
            '支持手动触发重新加载',
            '支持启用/禁用热更新功能'
        ],
        'monitored_dirs': [
            'src/common/',
            'src/testcase/',
            'src/pages/',
            'src/base/'
        ],
        'reloaded_modules': [
            'src.common.config_loader',
            'src.common.module_definition_loader',
            'src.common.database',
            'src.common.logger',
            'src.common.version_control'
        ],
        'notes': [
            'app.py 主文件修改后仍需手动重启服务',
            '修改配置文件后会自动重新加载',
            '热更新只影响新的请求，不影响正在执行的请求'
        ]
    })


@app.route('/get_logs/<int:execution_id>', methods=['GET'])
def get_logs(execution_id):
    """获取日志API"""
    try:
        db = get_db_instance()
        if db.connect():
            # 获取执行信息
            execution = db.get_execution_by_id(execution_id)
            db.close()
            
            if not execution:
                return jsonify({
                    'success': False,
                    'message': f'未找到执行ID为 {execution_id} 的记录'
                })
            
            # 构建日志文件匹配模式
            config = config_loader.get_config()
            logs_dir = os.path.join(os.path.dirname(__file__), config['paths']['logs_root_dir'])
            
            # 获取执行时间的时间戳部分（格式：%Y%m%d_%H%M%S）
            import datetime
            if isinstance(execution['start_time'], datetime.datetime):
                start_time = execution['start_time']
            else:
                start_time = None
                ts_str = str(execution['start_time'])
                for fmt in ['%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S']:
                    try:
                        start_time = datetime.datetime.strptime(ts_str, fmt)
                        break
                    except ValueError:
                        continue
                if not start_time:
                    start_time = datetime.datetime.now()
            date_str = start_time.strftime('%Y%m%d')
            time_str = start_time.strftime('%H%M%S')
            
            # 根据case参数构建日志文件名模式
            case_name = execution['case'] if execution['case'] else 'all'
            log_pattern = f'run_{case_name}_{date_str}_{time_str}*.log'
            
            # 查找匹配的日志文件
            import glob
            log_files = glob.glob(os.path.join(logs_dir, log_pattern))
            
            if not log_files:
                # 如果没有找到精确匹配的文件，尝试查找当天的所有日志文件
                log_pattern = f'run_{case_name}_{date_str}_*.log'
                log_files = glob.glob(os.path.join(logs_dir, log_pattern))
                
                if not log_files:
                    return jsonify({
                        'success': False,
                        'message': f'未找到执行ID为 {execution_id} 的日志文件'
                    })
            
            # 返回最新的日志文件
            log_path = sorted(log_files, key=os.path.getmtime, reverse=True)[0]
            
            # 读取日志内容，处理不同编码
            try:
                # 尝试使用utf-8编码
                with open(log_path, 'r', encoding='utf-8') as f:
                    log_content = f.read()
            except UnicodeDecodeError:
                try:
                    # 尝试使用gbk编码（Windows系统常用）
                    with open(log_path, 'r', encoding='gbk') as f:
                        log_content = f.read()
                except UnicodeDecodeError:
                    # 最后尝试使用latin-1编码，忽略无法解码的字符
                    with open(log_path, 'r', encoding='latin-1') as f:
                        log_content = f.read()
            
            # 提供分页或限制大小的参数
            page = request.args.get('page', 1, type=int)
            page_size = request.args.get('page_size', 100, type=int)
            max_length = request.args.get('max_length', 100000, type=int)  # 最大返回长度
            
            # 如果超过最大长度，只返回最后部分
            if len(log_content) > max_length:
                log_content = log_content[-max_length:]
                truncated = True
            else:
                truncated = False
            
            # 如果需要分页
            if page > 1:
                lines = log_content.splitlines()
                start_index = (page - 1) * page_size
                end_index = start_index + page_size
                log_content = '\n'.join(lines[start_index:end_index])
                total_pages = (len(lines) + page_size - 1) // page_size
            else:
                total_pages = 1
            
            return jsonify({
                'success': True,
                'execution_id': execution_id,
                'log_content': log_content,
                'file_path': log_path,
                'file_size': os.path.getsize(log_path),
                'truncated': truncated,
                'current_page': page,
                'page_size': page_size,
                'total_pages': total_pages
            })
        else:
            return jsonify({
                'success': False,
                'message': '数据库连接失败'
            })
    except Exception as e:
        logger.error(f'获取日志失败: {str(e)}')
        return jsonify({
            'success': False,
            'message': f'获取日志失败: {str(e)}'
        })


# ==================== 测试计划相关路由 ====================

@app.route('/plans')
def plan_list():
    """测试计划页面"""
    db = get_db_instance()
    plans = []
    grouped_cases_json = []
    if db.connect():
        plans = db.get_all_plans()
        all_cases = db.get_all_case_info()
        db.close()

        # 按项目→模块分组用例，供选择用例使用
        grouped_cases = {}
        for case in all_cases:
            project = case.get('project', '') or ''
            module = case.get('module', '') or ''
            grouped_cases.setdefault(project, {}).setdefault(module, []).append({
                'case_name': case.get('case_name', ''),
                'case_scene': case.get('case_scene', '') or ''
            })

        for project in sorted(grouped_cases.keys()):
            modules_list = []
            for module in sorted(grouped_cases[project].keys()):
                modules_list.append({
                    'name': module,
                    'name_cn': module_def_loader.get_module_name_cn(module),
                    'cases': grouped_cases[project][module]
                })
            grouped_cases_json.append({
                'name': project,
                'name_cn': module_def_loader.get_project_name_cn(project),
                'modules': modules_list
            })

    return render_template('test_plan.html',
                           plans=plans,
                           grouped_cases_json=grouped_cases_json)


@app.route('/api/plan/list', methods=['GET'])
def api_plan_list():
    """获取测试计划列表"""
    db = get_db_instance()
    if db.connect():
        plans = db.get_all_plans()
        db.close()
        return jsonify({'success': True, 'plans': plans})
    return jsonify({'success': False, 'message': '数据库连接失败', 'plans': []})


@app.route('/api/plan/<int:plan_id>', methods=['GET'])
def api_plan_detail(plan_id):
    """获取单个测试计划详情（含已绑定用例）"""
    db = get_db_instance()
    if db.connect():
        plan = db.get_plan_by_id(plan_id)
        if not plan:
            db.close()
            return jsonify({'success': False, 'message': f'未找到计划 {plan_id}'})
        case_names = db.get_cases_by_plan(plan_id)
        db.close()
        plan['case_names'] = case_names
        return jsonify({'success': True, 'plan': plan})
    return jsonify({'success': False, 'message': '数据库连接失败'})


@app.route('/api/plan/create', methods=['POST'])
def api_plan_create():
    """新建测试计划"""
    data = request.get_json() or {}
    plan_name = (data.get('plan_name') or '').strip()
    description = data.get('description')
    creator = data.get('creator')
    case_names = data.get('case_names') or []

    if not plan_name:
        return jsonify({'success': False, 'message': '计划名称不能为空'})

    db = get_db_instance()
    if not db.connect():
        return jsonify({'success': False, 'message': '数据库连接失败'})
    try:
        # 计划名称唯一性校验
        if db.get_plan_by_name(plan_name):
            return jsonify({'success': False, 'message': '计划名称已存在，请更换'})

        plan_id = db.create_plan(plan_name, description, creator)
        if plan_id == -1:
            return jsonify({'success': False, 'message': '创建计划失败'})

        if case_names:
            db.update_plan_cases(plan_id, case_names)
        return jsonify({'success': True, 'message': '计划创建成功', 'plan_id': plan_id})
    finally:
        db.close()


@app.route('/api/plan/update', methods=['POST'])
def api_plan_update():
    """编辑测试计划（仅用例集合与描述，计划名称不可改）"""
    data = request.get_json() or {}
    plan_id = data.get('plan_id')
    case_names = data.get('case_names')
    description = data.get('description')

    if not plan_id:
        return jsonify({'success': False, 'message': '缺少 plan_id'})

    db = get_db_instance()
    if not db.connect():
        return jsonify({'success': False, 'message': '数据库连接失败'})
    try:
        plan = db.get_plan_by_id(plan_id)
        if not plan:
            return jsonify({'success': False, 'message': f'未找到计划 {plan_id}'})

        if description is not None:
            db.update_plan_desc(plan_id, description)
        if case_names is not None:
            db.update_plan_cases(plan_id, case_names)
        return jsonify({'success': True, 'message': '计划更新成功'})
    finally:
        db.close()


@app.route('/api/plan/delete', methods=['POST'])
def api_plan_delete():
    """删除测试计划（软删除）"""
    data = request.get_json() or {}
    plan_id = data.get('plan_id')
    if not plan_id:
        return jsonify({'success': False, 'message': '缺少 plan_id'})

    db = get_db_instance()
    if not db.connect():
        return jsonify({'success': False, 'message': '数据库连接失败'})
    try:
        if db.delete_plan(plan_id):
            return jsonify({'success': True, 'message': '计划已删除'})
        return jsonify({'success': False, 'message': '删除失败'})
    finally:
        db.close()


@app.route('/execute_plan', methods=['POST'])
def execute_plan():
    """执行测试计划：调用 run.py --plan_name，复用 EXECUTION_ID 协议"""
    try:
        params = request.json or {}
        plan_name = (params.get('plan_name') or '').strip()
        if not plan_name:
            return jsonify({'success': False, 'message': '计划名称不能为空'})

        cmd = ['python', 'run.py', '--plan_name', plan_name]
        command_str = ' '.join(cmd)
        execution_id = -1

        process = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(__file__),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        deadline = time.time() + 30
        while time.time() < deadline:
            line = process.stdout.readline()
            if not line:
                break
            line = line.strip()
            if line.startswith('EXECUTION_ID:'):
                try:
                    execution_id = int(line.split(':')[1])
                except ValueError:
                    pass
                break

        def consume_output():
            for _ in process.stdout:
                pass
            process.wait()

        threading.Thread(target=consume_output, daemon=True).start()

        response_data = {
            'success': True,
            'message': '测试计划执行已启动',
            'command': command_str
        }
        if execution_id != -1:
            response_data['execution_id'] = execution_id
        else:
            response_data['warning'] = '无法创建执行记录，可能是计划无有效用例或数据库连接失败'
        return jsonify(response_data)

    except Exception as e:
        logger.error(f'执行测试计划失败: {str(e)}')
        return jsonify({'success': False, 'message': f'执行失败: {str(e)}'})


# ==================== 版本管理相关路由 ====================

@app.route('/version_management')
def version_management():
    """版本管理页面"""
    current_version = get_current_version()
    versions = get_all_versions()
    return render_template('version_management.html',
                           current_version=current_version,
                           versions=versions)


@app.route('/api/version/check_exists', methods=['POST'])
def check_version_exists_api():
    """检查版本是否已存在"""
    data = request.get_json()
    version = data.get('version')
    
    if not version:
        return jsonify({'success': False, 'message': '版本号不能为空'})
    
    exists = check_version_exists(version)
    return jsonify({
        'success': True,
        'exists': exists,
        'info': get_version_info(version) if exists else None
    })


@app.route('/api/version/backup', methods=['POST'])
def backup_version_api():
    """备份当前版本"""
    data = request.get_json()
    backup_user = data.get('backup_user')
    version_info = data.get('version_info')
    
    if not backup_user:
        return jsonify({'success': False, 'message': '备份人不能为空'})
    
    try:
        success = backup_version(backup_user, version_info)
        if success:
            return jsonify({'success': True, 'message': '备份成功'})
        else:
            return jsonify({'success': False, 'message': '备份失败'})
    except Exception as e:
        logger.error(f'备份失败: {e}')
        return jsonify({'success': False, 'message': f'备份失败: {str(e)}'})


@app.route('/api/version/create', methods=['POST'])
def create_version_api():
    """创建新版本"""
    data = request.get_json()
    new_version = data.get('new_version')
    backup_user = data.get('backup_user')
    version_info = data.get('version_info')
    
    if not new_version or not backup_user:
        return jsonify({'success': False, 'message': '版本号和备份人不能为空'})
    
    # 检查版本是否已存在
    if check_version_exists(new_version):
        return jsonify({
            'success': False,
            'message': '该版本已有备份，请走备份流程或更换版本号'
        })
    
    try:
        success = create_new_version_with_info(new_version, backup_user, version_info)
        if success:
            return jsonify({'success': True, 'message': '新建成功'})
        else:
            return jsonify({'success': False, 'message': '新建失败'})
    except Exception as e:
        logger.error(f'新建版本失败: {e}')
        return jsonify({'success': False, 'message': f'新建失败: {str(e)}'})


@app.route('/api/version/switch', methods=['POST'])
def switch_version_api():
    """切换版本"""
    data = request.get_json()
    target_version = data.get('target_version')
    switch_user = data.get('switch_user')
    
    if not target_version or not switch_user:
        return jsonify({'success': False, 'message': '版本号和操作人不能为空'})
    
    try:
        success = switch_version(target_version)
        if success:
            return jsonify({'success': True, 'message': '切换成功'})
        else:
            return jsonify({'success': False, 'message': '切换失败'})
    except Exception as e:
        logger.error(f'切换版本失败: {e}')
        return jsonify({'success': False, 'message': f'切换失败: {str(e)}'})


@app.route('/api/version/delete', methods=['POST'])
def delete_version_api():
    """删除版本"""
    data = request.get_json()
    version = data.get('version')
    delete_user = data.get('delete_user')
    
    if not version or not delete_user:
        return jsonify({'success': False, 'message': '版本号和操作人不能为空'})
    
    try:
        success = delete_version(version, delete_user)
        if success:
            return jsonify({'success': True, 'message': '删除成功'})
        else:
            return jsonify({'success': False, 'message': '删除失败'})
    except Exception as e:
        logger.error(f'删除版本失败: {e}')
        return jsonify({'success': False, 'message': f'删除失败: {str(e)}'})


@app.route('/api/version/current_info', methods=['GET'])
def get_current_version_info_api():
    """获取当前版本详细信息"""
    current_version = get_current_version()
    if not current_version:
        return jsonify({'success': True, 'exists': False, 'info': None})
    
    info = get_version_info(current_version)
    return jsonify({
        'success': True,
        'exists': info is not None,
        'info': info,
        'current_version': current_version
    })


@app.route('/api/version/list', methods=['GET'])
def get_version_list_api():
    """获取版本列表"""
    versions = get_all_versions()
    return jsonify({'success': True, 'versions': versions})


# ==================== 用例修复相关 API ====================

import glob
from src.common.ai_fix_case import execute_fix_task


def _find_case_file(case_name):
    """根据用例名称查找用例源文件"""
    pattern = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           'src', 'testcase', '**', f'test_{case_name}.py')
    matches = glob.glob(pattern, recursive=True)
    if matches:
        return matches[0]
    return None



@app.route('/api/fix_case/start', methods=['POST'])
def fix_case_start():
    """启动用例修复任务

    若已存在该用例的修复任务，则重置为进行中（清空结果与结束时间，更新开始时间），
    否则新增一条修复任务。随后启动后台线程调用AI进行分析。
    """
    try:
        data = request.json or {}
        execution_id = data.get('execution_id')
        case_name = data.get('case_name')
        project = data.get('project', '')
        # 补充信息（非必填，前端已限制 300 字，后端再兜底截断）
        supplement_info = (data.get('supplement_info') or '').strip()
        if len(supplement_info) > 300:
            supplement_info = supplement_info[:300]

        if not case_name or not execution_id:
            return jsonify({'success': False, 'message': '缺少必要参数: case_name 或 execution_id'})

        # 获取用例源代码
        case_file = _find_case_file(case_name)
        if not case_file:
            return jsonify({'success': False, 'message': f'未找到用例文件: test_{case_name}.py'})
        with open(case_file, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # 获取失败日志和错误信息
        db = get_db_instance()
        if not db.connect():
            return jsonify({'success': False, 'message': '数据库连接失败'})
        try:
            case_results = db.get_case_results_by_execution(execution_id)
            target_case = None
            for cr in case_results:
                if case_name in cr.get('case_name', ''):
                    target_case = cr
                    break
            if not target_case:
                return jsonify({'success': False, 'message': f'未找到执行记录 {execution_id} 中的用例 {case_name}'})

            error_log = target_case.get('log', '')
            error_message = target_case.get('error_message', '')

            # 查询是否已有该用例的修复任务
            existing_task = db.get_fix_task_by_case(project, case_name, execution_id)
            if existing_task:
                # 已有任务，重置为进行中
                task_id = existing_task['id']
                if not db.reset_fix_task(task_id):
                    return jsonify({'success': False, 'message': '重置修复任务失败'})
            else:
                # 新增修复任务
                task_id = db.insert_fix_task(project, case_name, execution_id, source_code)
                if task_id == -1:
                    return jsonify({'success': False, 'message': '创建修复任务失败'})
        finally:
            db.close()

        # 启动后台线程（5分钟超时）
        def _run_with_timeout():
            result_holder = [None]
            def _target():
                result_holder[0] = 'done'
                # 子线程独立创建 db 实例，由 execute_fix_task 使用并由本线程关闭
                fix_db = get_db_instance()
                if not fix_db.connect():
                    logger.error(f"修复任务 {task_id}: 数据库连接失败")
                    return
                try:
                    execute_fix_task(task_id, source_code, error_log, error_message, fix_db, supplement_info)
                finally:
                    fix_db.close()
            t = threading.Thread(target=_target, daemon=True)
            t.start()
            t.join(timeout=300)  # 5分钟
            if t.is_alive():
                # 超时，更新任务状态为失败
                db2 = get_db_instance()
                if db2.connect():
                    try:
                        db2.update_fix_task_status(task_id, '失败')
                    finally:
                        db2.close()
                logger.error(f"修复任务 {task_id}: 超时5分钟未完成，判定失败")

        thread = threading.Thread(target=_run_with_timeout, daemon=True)
        thread.start()

        return jsonify({'success': True, 'task_id': task_id, 'message': '修复任务已启动'})
    except Exception as e:
        logger.error(f'启动用例修复失败: {str(e)}')
        return jsonify({'success': False, 'message': f'启动失败: {str(e)}'})


@app.route('/api/fix_case/query', methods=['GET'])
def fix_case_query():
    """根据项目、用例名称、执行ID查询已有修复任务"""
    try:
        execution_id = request.args.get('execution_id')
        case_name = request.args.get('case_name')
        project = request.args.get('project', '')
        if not case_name or not execution_id:
            return jsonify({'success': False, 'message': '缺少必要参数: case_name 或 execution_id'})
        try:
            execution_id = int(execution_id)
        except (TypeError, ValueError):
            return jsonify({'success': False, 'message': 'execution_id 必须为整数'})

        db = get_db_instance()
        if not db.connect():
            return jsonify({'success': False, 'message': '数据库连接失败'})
        try:
            task = db.get_fix_task_by_case(project, case_name, execution_id)
            return jsonify({'success': True, 'task': task})
        finally:
            db.close()
    except Exception as e:
        logger.error(f'查询用例修复任务失败: {str(e)}')
        return jsonify({'success': False, 'message': f'查询失败: {str(e)}'})


@app.route('/api/fix_case/status/<int:task_id>', methods=['GET'])
def fix_case_status(task_id):
    """查询修复任务状态"""
    db = get_db_instance()
    if not db.connect():
        return jsonify({'success': False, 'message': '数据库连接失败'})
    try:
        task = db.get_fix_task(task_id)
        if not task:
            return jsonify({'success': False, 'message': f'未找到修复任务 {task_id}'})
        return jsonify({'success': True, 'task': task})
    finally:
        db.close()


# 添加导航栏链接
@app.context_processor
def inject_nav_links():
    """注入导航链接"""
    return {
        'nav_items': [
            {'name': '用例列表', 'url': '/cases', 'active': 'cases'},
            {'name': '测试计划', 'url': '/plans', 'active': 'plans'},
            {'name': '执行记录', 'url': '/executions', 'active': 'executions'},
            {'name': '版本管理', 'url': '/version_management', 'active': 'version_management'}
        ]
    }


def cleanup_on_exit():
    """
    程序退出时的清理工作
    """
    stop_file_watcher()
    logger.info("服务已停止")


if __name__ == '__main__':
    init_db()
    
    print("=" * 60)
    print("测试用例管理系统")
    print("=" * 60)
    print("\n启动 Flask 服务器...")
    
    # 启动热更新监控器
    start_file_watcher()
    if _hot_reload_enabled and WATCHDOG_AVAILABLE:
        print("✓ 热更新功能已启用")
    elif not WATCHDOG_AVAILABLE:
        print("⚠ watchdog 未安装，热更新功能不可用")
    else:
        print("✓ 热更新功能已禁用")
    
    print(f"\n访问地址: http://localhost:5000")
    print(f"用例列表: http://localhost:5000/cases")
    print(f"执行记录: http://localhost:5000/executions")
    print(f"版本管理: http://localhost:5000/version_management")
    print(f"热更新状态: http://localhost:5000/hot_reload/status")
    print("\n按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        app.run(debug=True, use_reloader=False, host='0.0.0.0', port=5000)
    finally:
        cleanup_on_exit()
