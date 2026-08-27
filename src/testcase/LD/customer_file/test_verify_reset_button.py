import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyResetButton(BaseTest):
    """
    用例名：verify_reset_button
    用例ms的id：101254
    """

    def test_verify_reset_button(self, page: Page, project_name: str):
        f"""测试客户档案重置按钮功能
        用例名：verify_reset_button
        用例ms的id：101254
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_reset_button")
        logger.info(f"用例ms的id：101254")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入客户档案页面
        logger.info("进入客户档案页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("客户档案").click()
        
        # 输入查询条件，测试重置按钮功能
        logger.info("输入客户编码执行查询，点击重置按钮")
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        frame.get_by_role("textbox", name="客户编码 :").click()
        frame.get_by_role("textbox", name="客户编码 :").fill("KS202604230022")
        frame.get_by_role("button", name="查 询").click()
        frame.get_by_role("button", name="重 置").click()

        logger.info("verify_reset_button用例执行完成")