import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyEditButton(BaseTest):
    """
    用例名：verify_edit_button
    用例ms的id：101252
    """

    def test_verify_edit_button(self, page: Page, project_name: str):
        f"""测试客户档案编辑按钮功能
        用例名：verify_edit_button
        用例ms的id：101252
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_edit_button")
        logger.info(f"用例ms的id：101252")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        logger.info("执行系统登录")
        self.login(page, project_name)
        
        # 导航进入客户档案页面
        logger.info("导航进入客户档案页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("客户档案").click()
        
        # 选中目标客户并点击编辑
        logger.info("点击编辑按钮")
        content_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        content_frame.get_by_text("编辑").first.click()
        content_frame.get_by_role("button", name="close").first.click()
        
        logger.info("用例verify_edit_button执行完成")