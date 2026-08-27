import os
import time
from typing import Optional
from playwright.sync_api import Page, Response
from src.common.file_utils import FileUtils
from src.common.logger import logger


class ScreenshotUtils:
    """截图工具类"""
    
    @staticmethod
    def get_screenshot_dir(
        execution_timestamp: str,
        project_name: str,
        module_name: str,
        case_name: str,
        screenshots_root: str = "screenshots"
    ) -> str:
        """获取截图目录
        
        目录结构: screenshots/{execution_timestamp}/{project}/{module}/{case_name}/
        
        Args:
            execution_timestamp: 执行时间戳
            project_name: 项目名称
            module_name: 模块名称
            case_name: 用例名称
            screenshots_root: 截图根目录
            
        Returns:
            截图目录路径
        """
        screenshot_dir = os.path.join(
            screenshots_root,
            execution_timestamp,
            project_name,
            module_name,
            case_name
        )
        FileUtils.create_directory(screenshot_dir)
        logger.info(f"用例截图目录: {screenshot_dir}")
        return screenshot_dir
    
    @staticmethod
    def take_error_screenshot(
        page: Page,
        screenshot_dir: str,
        case_name: str,
        error: Exception
    ) -> str:
        """拍摄错误截图
        
        Args:
            page: Playwright Page对象
            screenshot_dir: 截图目录
            case_name: 用例名称
            error: 异常对象
            
        Returns:
            截图文件路径
        """
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S") + "_" + str(int(time.time() * 1000000))[-6:]
            error_name = str(error.__class__.__name__)
            filename = f"{timestamp}_failure_{case_name}_{error_name}.png"
            file_path = os.path.join(screenshot_dir, filename)
            
            page.screenshot(path=file_path, full_page=True)
            logger.info(f"错误截图已保存: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"错误截图失败: {str(e)}")
            return ""
    
    @staticmethod
    def take_page_status_screenshot(
        page: Page,
        screenshot_dir: str,
        case_name: str,
        status_code: int
    ) -> str:
        """拍摄页面状态错误截图（例如404、400等）
        
        Args:
            page: Playwright Page对象
            screenshot_dir: 截图目录
            case_name: 用例名称
            status_code: 状态码
            
        Returns:
            截图文件路径
        """
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S") + "_" + str(int(time.time() * 1000000))[-6:]
            filename = f"{timestamp}_page_error_{case_name}_status{status_code}.png"
            file_path = os.path.join(screenshot_dir, filename)
            
            page.screenshot(path=file_path, full_page=True)
            logger.info(f"页面状态错误截图已保存: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"页面状态错误截图失败: {str(e)}")
            return ""
