import os
import time
import shutil
import pytest
from src.common.file_utils import FileUtils
from src.common.config_loader import config_loader
from src.common.logger import logger


EXECUTION_TIMESTAMP = None


def get_execution_timestamp():
    """获取执行时间戳，同一批次执行共享"""
    global EXECUTION_TIMESTAMP
    if EXECUTION_TIMESTAMP is None:
        EXECUTION_TIMESTAMP = time.strftime("%Y%m%d_%H%M%S")
    return EXECUTION_TIMESTAMP


@pytest.fixture(scope="session")
def execution_timestamp():
    """会话级执行时间戳"""
    return get_execution_timestamp()


def safe_remove_file(filepath, max_retries=3, retry_delay=1):
    """安全删除文件，支持重试
    
    Args:
        filepath: 要删除的文件路径
        max_retries: 最大重试次数
        retry_delay: 重试间隔（秒）
    
    Returns:
        bool: 删除成功返回True，否则返回False
    """
    for attempt in range(max_retries):
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                logger.debug(f"成功删除文件: {filepath}")
                return True
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                logger.debug(f"删除文件失败（尝试 {attempt + 1}/{max_retries}）: {filepath}, 错误: {e}")
                time.sleep(retry_delay)
            else:
                logger.warning(f"删除文件失败（已重试 {max_retries} 次）: {filepath}, 错误: {e}")
                return False


def safe_remove_dir(dirpath, max_retries=3, retry_delay=2):
    """安全删除目录，支持重试
    
    Args:
        dirpath: 要删除的目录路径
        max_retries: 最大重试次数
        retry_delay: 重试间隔（秒）
    
    Returns:
        bool: 删除成功返回True，否则返回False
    """
    for attempt in range(max_retries):
        try:
            if os.path.exists(dirpath):
                # 先尝试删除目录内的所有文件
                for root, dirs, files in os.walk(dirpath):
                    for file in files:
                        filepath = os.path.join(root, file)
                        safe_remove_file(filepath, max_retries=2, retry_delay=0.5)
                
                # 然后删除空目录
                shutil.rmtree(dirpath)
                logger.debug(f"成功删除目录: {dirpath}")
                return True
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                logger.debug(f"删除目录失败（尝试 {attempt + 1}/{max_retries}）: {dirpath}, 错误: {e}")
                time.sleep(retry_delay)
            else:
                logger.warning(f"删除目录失败（已重试 {max_retries} 次）: {dirpath}, 错误: {e}")
                return False


def handle_video_recording(case_name: str, execution_ts: str, is_failed: bool):
    """根据用例执行结果处理视频录制
    
    策略：执行完一条判断一条
      - 成功：删除视频目录
      - 失败：保留视频
    
    Args:
        case_name: 用例名称
        execution_ts: 执行时间戳
        is_failed: 是否失败
    """
    config = config_loader.get_config()
    enable_video_record = config['global'].get('enable_video_record', False)
    
    if not enable_video_record:
        return
    
    videos_root_dir = config['paths'].get('videos_root_dir', 'videos')
    case_video_dir = os.path.join(
        videos_root_dir,
        execution_ts,
        case_name
    )
    
    if not os.path.exists(case_video_dir):
        logger.debug(f"视频目录不存在: {case_video_dir}")
        return
    
    if is_failed:
        logger.info(f"用例执行失败，保留视频: {case_video_dir}")
    else:
        # 用例执行成功，等待一段时间让 Playwright 释放视频文件
        # 然后尝试安全删除视频目录
        try:
            # 等待1.5秒让 Playwright 完全释放文件
            time.sleep(1.5)
            
            if safe_remove_dir(case_video_dir, max_retries=3, retry_delay=2):
                logger.info(f"用例执行成功，删除视频: {case_video_dir}")
            else:
                logger.warning(f"删除视频失败，文件可能被占用: {case_video_dir}")
        except Exception as e:
            logger.warning(f"删除视频失败: {e}")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """用例执行报告钩子"""
    outcome = yield
    report = outcome.get_result()
    
    # 视频处理已移至 base_test.py 中的 context fixture
    # 在 context.close() 之后执行，确保视频文件被完全释放
    pass


@pytest.fixture(scope="session", autouse=True)
def setup_execution_timestamp():
    """会话级fixture，初始化执行时间戳"""
    get_execution_timestamp()
    logger.info(f"测试执行时间戳: {EXECUTION_TIMESTAMP}")
    yield
