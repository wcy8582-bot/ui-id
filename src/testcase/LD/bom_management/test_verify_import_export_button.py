import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyImportExportButton(BaseTest):
    """
    用例名：verify_import_export_button
    用例ms的id：101312
    """

    def test_verify_import_export_button(self, page: Page, project_name: str):
        f"""验证物料清单页面导入导出按钮显示正常
        用例名：verify_import_export_button
        用例ms的id：101312
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_import_export_button")
        logger.info(f"用例ms的id：101312")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法完成登录
        self.login(page, project_name)


        # 导航进入物料清单功能页面
        logger.info("进入物料清单页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("物料清单").click()

        # 验证导入、导出按钮可见
        logger.info("验证导入导出按钮可见性")
        expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="import 导入")).to_be_visible()
        expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="export 导出")).to_be_visible()
        
        logger.info(f"用例verify_import_export_button执行完成")