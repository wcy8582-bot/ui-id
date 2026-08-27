import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyCreateMobileCardSettings(BaseTest):
    """
    用例名：verify_create_settings
    用例ms的id：100791
    """

    def test_verify_create_settings(self, page: Page, project_name: str):
        f"""测试新增移动端卡片配置功能
        用例名：verify_create_settings
        用例ms的id：100791
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_create_settings")
        logger.info(f"用例ms的id：100791")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法
        logger.info("执行系统登录")
        self.login(page, project_name)
        
        # 导航到移动端卡片配置页面
        logger.info("导航到移动端卡片配置页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("系统配置").click()
        page.get_by_text("移动端卡片配置").click()
        
        # 获取iframe上下文，点击新增模板按钮
        logger.info("点击新增模板按钮")
        card_iframe = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        card_iframe.get_by_role("button", name="plus-circle 新增模板").click()
        
        # 勾选需要展示的配置字段
        logger.info("配置模板展示字段")
        card_iframe.locator("label").filter(has_text="工单编号").click()
        card_iframe.get_by_role("checkbox", name="产品信息").check()
        card_iframe.get_by_role("checkbox", name="工序编码").check()
        card_iframe.get_by_role("checkbox", name="工序名称").check()
        
        logger.info("用例verify_create_settings执行完成")