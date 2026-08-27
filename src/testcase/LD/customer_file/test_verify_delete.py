import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyDelete(BaseTest):
    """
    用例名：verify_delete
    用例ms的id：101263、101235
    """

    def test_verify_delete(self, page: Page, project_name: str):
        f"""测试删除已启用客商功能
        用例名：verify_delete
        用例ms的id：101263、101235
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_delete")
        logger.info(f"用例ms的id：101263")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法登录系统
        logger.info("执行系统登录")
        self.login(page, project_name)
        
        # 导航进入客户档案页面
        logger.info("进入客户档案模块")
        page.get_by_text("基础资料").click()
        page.get_by_text("客户档案").click()
        
        # 执行删除操作，验证禁用客商删除提示
        logger.info("执行删除目标客商操作，验证提示信息")
        content_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        content_frame.get_by_text("删除").first.click()
        page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="确 定").click()
        page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("div").filter(has_text="客商已启用，不可删除！").nth(3).click()
        
        # 验证提示符合预期
        expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_text("客商已启用，不可删除！")).to_be_visible()
        logger.info("验证完成：正确弹出「客商已启用，不可删除！」提示")
        logger.info(f"用例verify_delete执行完毕")