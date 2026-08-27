import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestVerifyDeleteFunction(BaseTest):
    """
    用例名：verify_delete_function
    用例ms的id：101140
    """

    def test_verify_delete_function(self, page: Page, project_name: str):
        f"""测试删除功能验证
        用例名：verify_delete_function
        用例ms的id：101140
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行verify_delete_function")
        logger.info(f"用例ms的id：101140")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法登录系统
        logger.info("登录目标系统")
        self.login(page, project_name)
        
        # 导航进入打印机管理菜单
        logger.info("导航到打印机管理页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("系统配置").click()
        page.get_by_text("打印机管理").click()

        # 获取iframe内容实例，开始验证删除功能
        logger.info("开始验证删除功能流程")
        delete_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 等待列表加载
        logger.info("等待打印机列表加载")
        page.wait_for_timeout(1000)
        
        # 验证取消删除流程
        logger.info("点击第一个'删除'按钮，验证取消操作")
        delete_frame.get_by_text("删除").first.click()
        delete_frame.get_by_role("button", name="取 消").click()
        
        # 验证确认删除流程
        logger.info("再次点击第一个'删除'按钮，验证确认操作")
        delete_frame.get_by_text("删除").first.click()
        delete_frame.get_by_role("button", name="确 定").click()

        logger.info("verify_delete_function 执行完成")