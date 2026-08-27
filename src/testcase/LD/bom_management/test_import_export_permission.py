import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestImportExportPermission(BaseTest):
    """
    用例名：import_export_permission
    用例ms的id：101316
    """

    def test_import_export_permission(self, page: Page, project_name: str):
        f"""测试物料清单导入导出按钮
        用例名：import_export_permission
        用例ms的id：101316
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：import_export_permission")
        logger.info(f"用例ms的id：101316")
        logger.info("=" * 60)
        
        # 使用公用登录方法登录系统
        logger.info("调用公用登录方法完成登录")
        self.login(page, project_name)
        
        # 导航进入物料清单页面
        logger.info("导航进入物料清单页面")
        page.locator("svg").nth(2).click()
        page.get_by_text("基础资料").click()
        page.get_by_text("物料清单").click()
        
        # 验证导入导出按钮可见且存在
        logger.info("验证导入、导出按钮存在且可见")
        content_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        expect(content_frame.locator("#root")).to_contain_text("导入")
        expect(content_frame.get_by_role("button", name="import 导入")).to_be_visible()
        expect(content_frame.locator("#root")).to_contain_text("导出")
        expect(content_frame.get_by_role("button", name="export 导出")).to_be_visible()
        
        logger.info(f"用例import_export_permission执行完成")