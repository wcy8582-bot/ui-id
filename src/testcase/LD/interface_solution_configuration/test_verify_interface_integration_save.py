import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyInterfaceIntegrationSave(BaseTest):
    """
    用例名：verify_interface_integration_save
    用例ms的id：100881
    """

    def test_verify_interface_integration_save(self, page: Page, project_name: str):
        f"""测试接口方案配置编辑保存功能
        用例名：verify_interface_integration_save
        用例ms的id：100881
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行verify_interface_integration_save")
        logger.info(f"用例ms的id：100881")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法完成登录
        logger.info("完成系统登录")
        self.login(page, project_name)

        # 导航到接口方案配置页面
        logger.info("导航进入接口方案配置页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("系统配置").click()
        page.get_by_text("接口方案配置").click()
        
        # 执行编辑保存操作
        logger.info("执行编辑后保存操作")
        config_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        config_frame.get_by_role("button", name="编 辑").click()
        config_frame.get_by_role("button", name="保 存").click()
        
        logger.info("verify_interface_integration_save用例执行完成")