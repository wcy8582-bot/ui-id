import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyCreatePage(BaseTest):
    """
    用例名：verify_create_page
    用例ms的id：101201
    """

    def test_verify_create_page(self, page: Page, project_name: str):
        f"""测试供应商档案新增页面打开功能
        用例名：verify_create_page
        用例ms的id：101201
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行verify_create_page")
        logger.info(f"用例ms的id：101201")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法
        self.login(page, project_name)
        
        # 导航进入供应商档案页面
        logger.info("点击基础资料菜单")
        page.get_by_text("基础资料").click()
        logger.info("点击供应商档案菜单")
        page.get_by_text("供应商档案").click()
        
        # 点击新增按钮打开新增页面
        logger.info("点击新增按钮")
        page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="plus-circle 新增").click()