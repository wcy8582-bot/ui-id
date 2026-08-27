from typing import Optional, List, Dict, Any
from playwright.sync_api import Page, Locator, expect
from src.common.logger import logger
from src.common.screenshot import ScreenshotUtils


class BasePage:
    """页面基类"""
    
    def __init__(self, page: Page):
        """初始化页面
        
        Args:
            page: Playwright Page对象
        """
        self.page = page
        self.screenshot_utils = ScreenshotUtils()
    
    def click(self, locator: Locator, timeout: Optional[int] = None) -> None:
        """点击元素
        
        Args:
            locator: 元素定位器
            timeout: 超时时间（毫秒）
        """
        try:
            logger.info(f"点击元素: {locator}")
            locator.click(timeout=timeout)
            logger.info(f"点击元素成功: {locator}")
        except Exception as e:
            logger.error(f"点击元素失败: {locator}, 错误: {str(e)}")
            raise
    
    def fill(self, locator: Locator, value: str, timeout: Optional[int] = None) -> None:
        """输入文本
        
        Args:
            locator: 元素定位器
            value: 输入值
            timeout: 超时时间（毫秒）
        """
        try:
            logger.info(f"输入文本: {locator}, 值: {value}")
            locator.fill(value, timeout=timeout)
            logger.info(f"输入文本成功: {locator}")
        except Exception as e:
            logger.error(f"输入文本失败: {locator}, 错误: {str(e)}")
            raise
    
    def clear(self, locator: Locator, timeout: Optional[int] = None) -> None:
        """清空输入框
        
        Args:
            locator: 元素定位器
            timeout: 超时时间（毫秒）
        """
        try:
            logger.info(f"清空输入框: {locator}")
            locator.clear(timeout=timeout)
            logger.info(f"清空输入框成功: {locator}")
        except Exception as e:
            logger.error(f"清空输入框失败: {locator}, 错误: {str(e)}")
            raise
    
    def select_option(self, locator: Locator, option: str, timeout: Optional[int] = None) -> None:
        """选择下拉选项
        
        Args:
            locator: 元素定位器
            option: 选项值
            timeout: 超时时间（毫秒）
        """
        try:
            logger.info(f"选择下拉选项: {locator}, 选项: {option}")
            locator.select_option(option, timeout=timeout)
            logger.info(f"选择下拉选项成功: {locator}")
        except Exception as e:
            logger.error(f"选择下拉选项失败: {locator}, 错误: {str(e)}")
            raise
    
    def check(self, locator: Locator, timeout: Optional[int] = None) -> None:
        """勾选复选框
        
        Args:
            locator: 元素定位器
            timeout: 超时时间（毫秒）
        """
        try:
            logger.info(f"勾选复选框: {locator}")
            locator.check(timeout=timeout)
            logger.info(f"勾选复选框成功: {locator}")
        except Exception as e:
            logger.error(f"勾选复选框失败: {locator}, 错误: {str(e)}")
            raise
    
    def uncheck(self, locator: Locator, timeout: Optional[int] = None) -> None:
        """取消勾选复选框
        
        Args:
            locator: 元素定位器
            timeout: 超时时间（毫秒）
        """
        try:
            logger.info(f"取消勾选复选框: {locator}")
            locator.uncheck(timeout=timeout)
            logger.info(f"取消勾选复选框成功: {locator}")
        except Exception as e:
            logger.error(f"取消勾选复选框失败: {locator}, 错误: {str(e)}")
            raise
    
    def hover(self, locator: Locator, timeout: Optional[int] = None) -> None:
        """悬停元素
        
        Args:
            locator: 元素定位器
            timeout: 超时时间（毫秒）
        """
        try:
            logger.info(f"悬停元素: {locator}")
            locator.hover(timeout=timeout)
            logger.info(f"悬停元素成功: {locator}")
        except Exception as e:
            logger.error(f"悬停元素失败: {locator}, 错误: {str(e)}")
            raise
    
    def goto(self, url: str, timeout: Optional[int] = None) -> None:
        """跳转到指定URL
        
        Args:
            url: 目标URL
            timeout: 超时时间（毫秒）
        """
        try:
            logger.info(f"跳转到URL: {url}")
            self.page.goto(url, timeout=timeout)
            logger.info(f"跳转成功: {url}")
        except Exception as e:
            logger.error(f"跳转失败: {url}, 错误: {str(e)}")
            raise
    
    def reload(self, timeout: Optional[int] = None) -> None:
        """刷新页面
        
        Args:
            timeout: 超时时间（毫秒）
        """
        try:
            logger.info("刷新页面")
            self.page.reload(timeout=timeout)
            logger.info("刷新页面成功")
        except Exception as e:
            logger.error(f"刷新页面失败: {str(e)}")
            raise
    
    def go_back(self, timeout: Optional[int] = None) -> None:
        """返回上一页
        
        Args:
            timeout: 超时时间（毫秒）
        """
        try:
            logger.info("返回上一页")
            self.page.go_back(timeout=timeout)
            logger.info("返回上一页成功")
        except Exception as e:
            logger.error(f"返回上一页失败: {str(e)}")
            raise
    
    def go_forward(self, timeout: Optional[int] = None) -> None:
        """前进到下一页
        
        Args:
            timeout: 超时时间（毫秒）
        """
        try:
            logger.info("前进到下一页")
            self.page.go_forward(timeout=timeout)
            logger.info("前进到下一页成功")
        except Exception as e:
            logger.error(f"前进到下一页失败: {str(e)}")
            raise
    
    def switch_to_window(self, index: int = 0) -> None:
        """切换窗口
        
        Args:
            index: 窗口索引
        """
        try:
            logger.info(f"切换到窗口索引: {index}")
            self.page.context.pages[index].bring_to_front()
            self.page = self.page.context.pages[index]
            logger.info("切换窗口成功")
        except Exception as e:
            logger.error(f"切换窗口失败: {str(e)}")
            raise
    
    def switch_to_iframe(self, locator: Locator) -> None:
        """切换到iframe
        
        Args:
            locator: iframe定位器
        """
        try:
            logger.info(f"切换到iframe: {locator}")
            frame = locator.content_frame()
            self.page = frame
            logger.info("切换到iframe成功")
        except Exception as e:
            logger.error(f"切换到iframe失败: {str(e)}")
            raise
    
    def wait_for_load_state(self, state: str = "networkidle", timeout: Optional[int] = None) -> None:
        """等待页面加载状态
        
        Args:
            state: 加载状态（load, domcontentloaded, networkidle）
            timeout: 超时时间（毫秒）
        """
        try:
            logger.info(f"等待页面加载状态: {state}")
            self.page.wait_for_load_state(state, timeout=timeout)
            logger.info(f"页面加载状态完成: {state}")
        except Exception as e:
            logger.error(f"等待页面加载状态失败: {str(e)}")
            raise
    
    def wait_for_selector(self, selector: str, timeout: Optional[int] = None) -> Locator:
        """等待元素出现
        
        Args:
            selector: 元素选择器
            timeout: 超时时间（毫秒）
            
        Returns:
            元素定位器
        """
        try:
            logger.info(f"等待元素出现: {selector}")
            locator = self.page.locator(selector)
            locator.wait_for(timeout=timeout)
            logger.info(f"元素出现: {selector}")
            return locator
        except Exception as e:
            logger.error(f"等待元素出现失败: {selector}, 错误: {str(e)}")
            raise
    
    # 断言方法
    def assert_title(self, title: str) -> None:
        """断言页面标题
        
        Args:
            title: 预期标题
        """
        try:
            logger.info(f"断言页面标题: {title}")
            expect(self.page).to_have_title(title)
            logger.info("页面标题断言成功")
        except Exception as e:
            logger.error(f"页面标题断言失败: {str(e)}")
            raise
    
    def assert_url(self, url: str) -> None:
        """断言页面URL
        
        Args:
            url: 预期URL
        """
        try:
            logger.info(f"断言页面URL: {url}")
            expect(self.page).to_have_url(url)
            logger.info("页面URL断言成功")
        except Exception as e:
            logger.error(f"页面URL断言失败: {str(e)}")
            raise
    
    def assert_text(self, locator: Locator, text: str) -> None:
        """断言元素文本
        
        Args:
            locator: 元素定位器
            text: 预期文本
        """
        try:
            logger.info(f"断言元素文本: {locator}, 预期: {text}")
            expect(locator).to_have_text(text)
            logger.info("元素文本断言成功")
        except Exception as e:
            logger.error(f"元素文本断言失败: {str(e)}")
            raise
    
    def assert_visible(self, locator: Locator) -> None:
        """断言元素可见
        
        Args:
            locator: 元素定位器
        """
        try:
            logger.info(f"断言元素可见: {locator}")
            expect(locator).to_be_visible()
            logger.info("元素可见断言成功")
        except Exception as e:
            logger.error(f"元素可见断言失败: {str(e)}")
            raise
    
    def assert_exists(self, locator: Locator) -> None:
        """断言元素存在
        
        Args:
            locator: 元素定位器
        """
        try:
            logger.info(f"断言元素存在: {locator}")
            expect(locator).to_exist()
            logger.info("元素存在断言成功")
        except Exception as e:
            logger.error(f"元素存在断言失败: {str(e)}")
            raise
