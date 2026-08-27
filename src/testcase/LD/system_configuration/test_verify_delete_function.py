import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyDeleteFunction(BaseTest):
    """
    用例名：verify_delete_function
    用例ms的id：101116
    """

    def test_verify_delete_function(self, page: Page, project_name: str):
        f"""测试标签打印配置删除功能
        用例名：verify_delete_function
        用例ms的id：101116
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_delete_function")
        logger.info(f"用例ms的id：101116")
        logger.info("=" * 60)
        
        # 使用公用登录方法登录系统
        logger.info("调用公用登录方法登录系统")
        self.login(page, project_name)
        
        # 进入标签打印配置页面
        logger.info("登录完成，后续跳转进入标签打印配置页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("系统配置").click()
        page.get_by_text("标签打印配置").click()
        
        # 获取业务内容iframe，复用定位
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        logger.info("开始执行删除功能验证")

        # 场景1：删除第二条配置点击确认（索引1）
        logger.info("测试场景1：删除第二条配置，确认删除操作")
        frame.get_by_text("删除").nth(1).click()
        frame.get_by_role("button", name="确 定").click()

        # 场景2：删除第一条配置点击取消（索引0）
        logger.info("测试场景2：删除第一条配置，取消删除操作")
        frame.get_by_text("删除").nth(0).click()
        frame.get_by_role("button", name="取 消").click()
        
        logger.info("用例verify_delete_function执行完成")