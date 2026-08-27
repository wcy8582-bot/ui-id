import pytest
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
import allure
from typing import Generator, Optional
from src.common.logger import logger
from src.common.screenshot import ScreenshotUtils
from src.common.file_utils import FileUtils
from src.common.config_loader import config_loader


class BaseTest:
    """用例基类"""
    
    @pytest.fixture(scope="function")
    def browser(self) -> Generator[Browser, None, None]:
        """用例级浏览器实例
        
        Yields:
            浏览器实例
        """
        import asyncio
        # 确保不在asyncio循环中运行
        try:
            asyncio.get_running_loop()
            logger.warning("检测到asyncio循环正在运行，尝试在新线程中启动浏览器")
        except RuntimeError:
            pass
            
        config = config_loader.get_config()
        browser_type = config['browser']['browser_type']
        headless = config['browser']['headless']
        slow_mo = config['browser']['slow_mo']
        
        logger.info(f"启动浏览器: {browser_type}, 无头模式: {headless}")
        
        try:
            with sync_playwright() as p:
                if browser_type == "Chromium":
                    browser = p.chromium.launch(
                        headless=headless,
                        slow_mo=slow_mo,
                        args=["--no-sandbox", "--disable-setuid-sandbox"]
                    )
                elif browser_type == "Firefox":
                    browser = p.firefox.launch(
                        headless=headless,
                        slow_mo=slow_mo
                    )
                elif browser_type == "WebKit":
                    browser = p.webkit.launch(
                        headless=headless,
                        slow_mo=slow_mo
                    )
                else:
                    raise ValueError(f"不支持的浏览器类型: {browser_type}")
                
                yield browser
                
                logger.info("关闭浏览器")
                browser.close()
        except Exception as e:
            logger.error(f"浏览器操作失败: {str(e)}")
            raise
    
    @pytest.fixture(scope="function")
    def context(self, browser: Browser) -> Generator[BrowserContext, None, None]:
        """用例级浏览器上下文
        
        Args:
            browser: 浏览器实例
            
        Yields:
            浏览器上下文
        """
        config = config_loader.get_config()
        viewport_size = config['browser']['viewport_size']
        ignore_https_errors = config['browser']['ignore_https_errors']
        
        context = browser.new_context(
            viewport=viewport_size,
            ignore_https_errors=ignore_https_errors
        )
        
        yield context
        
        logger.info("关闭浏览器上下文")
        context.close()
    
    @pytest.fixture(scope="function")
    def project_name(self) -> str:
        """项目名称
        
        Returns:
            项目名称
        """
        import os
        return os.environ.get('PROJECT_NAME', 'default')
    
    @pytest.fixture(scope="function")
    def page(self, context: BrowserContext) -> Generator[Page, None, None]:
        """用例级页面实例
        
        Args:
            context: 浏览器上下文
            
        Yields:
            页面实例
        """
        page = context.new_page()
        yield page
        
        logger.info("关闭页面")
        page.close()
    
    @pytest.fixture(scope="function")
    def screenshot_dir(self, request) -> str:
        """截图目录
        
        Args:
            request: pytest请求对象
            
        Returns:
            截图目录路径
        """
        config = config_loader.get_config()
        screenshots_root = config['paths']['screenshots_root_dir']
        
        # 从测试用例路径中提取项目和模块信息
        test_path = request.node.fspath.strpath
        project_name = "default"
        module_name = "default"
        
        # 尝试从路径中提取项目和模块
        if "testcase" in test_path:
            parts = test_path.split("testcase")[-1].split(os.sep)
            if len(parts) >= 3:
                project_name = parts[1]
                module_name = parts[2]
        
        screenshot_dir = ScreenshotUtils.get_screenshot_dir(
            project_name,
            module_name,
            screenshots_root
        )
        
        return screenshot_dir
    
    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """用例执行报告钩子"""
        outcome = yield
        report = outcome.get_result()
        
        # 仅处理失败的用例
        if report.when == "call" and report.failed:
            # 获取页面实例
            for fixture_name in item.fixturenames:
                if fixture_name == "page":
                    page = item.funcargs.get(fixture_name)
                    if page:
                        # 获取截图目录
                        screenshot_dir = item.funcargs.get("screenshot_dir", "screenshots")
                        # 拍摄错误截图
                        case_name = item.name
                        error = call.excinfo.value
                        ScreenshotUtils.take_error_screenshot(
                            page,
                            screenshot_dir,
                            case_name,
                            error
                        )
                        break
    
    def setup_method(self):
        """测试方法前置"""
        logger.info(f"开始执行测试: {self.__class__.__name__}")
    
    def teardown_method(self):
        """测试方法后置"""
        logger.info(f"测试执行完成: {self.__class__.__name__}")
    
    def login(self, page, project_name):
        """公用登录方法
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        config = config_loader.get_config()
        
        # 获取项目登录信息
        if project_name not in config.get('project_login', {}):
            raise ValueError(f"项目 {project_name} 的登录信息未配置")
        
        login_config = config['project_login'][project_name]
        login_url = login_config['login_url']
        username = login_config['username']
        password = login_config['password']
        
        logger.info(f"开始登录 {project_name} 项目...")
        logger.info(f"登录URL: {login_url}")
        logger.info(f"用户名: {username}")
        
        # 执行登录流程
        page.goto(login_url)
        
        # 输入用户名
        page.get_by_role("textbox", name="请输入用户名").click()
        page.get_by_role("textbox", name="请输入用户名").fill(username)
        
        # 输入密码
        page.get_by_role("textbox", name="请输入密码").click()
        page.get_by_role("textbox", name="请输入密码").fill(password)
        
        # 点击登录
        page.get_by_role("button", name="登 录").click()
        
        # 等待页面加载
        page.wait_for_load_state('networkidle')
        
        # 自动处理在线用户超限提示弹窗
        try:
            logger.info("检查是否存在在线用户超限提示")
            confirm_btn = page.get_by_role("button", name="确定")
            if confirm_btn.is_visible(timeout=3000):
                confirm_btn.click()
                logger.info("已自动点击在线用户提示的确定按钮")
                page.wait_for_timeout(1000)
        except:
            pass
        
        # 检查是否有登录失败的错误信息
        try:
            # 检查用户名或密码错误
            error_element = page.get_by_text("用户名或密码错误")
            error_element.wait_for(timeout=5000)
            logger.error(f"{project_name} 项目登录失败: 用户名或密码错误")
            raise Exception(f"登录失败: 用户名或密码错误")
        except:
            # 没有错误信息，认为登录成功
            logger.info(f"{project_name} 项目登录成功！")

# 导入os模块
import os
