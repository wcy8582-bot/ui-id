import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyImportButton(BaseTest):
    """
    用例名：verify_import_button
    用例ms的id：101244
    """

    def test_verify_import_button(self, page: Page, project_name: str):
        f"""测试客户档案导入按钮验证
        用例名：verify_import_button
        用例ms的id：101244
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_import_button")
        logger.info(f"用例ms的id：101244")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法完成登录
        self.login(page, project_name)
        logger.info("系统登录完成")
        
        # 导航进入客户档案页面
        logger.info("导航进入客户档案页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("客户档案").click()
        
        # 点击导入按钮
        logger.info("点击导入按钮唤起导入弹窗")
        page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="import 导入").first.click()
        
        # 点击导入说明文本区域
        logger.info("点击导入说明区域完成交互")
        page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("div").filter(has_text="文件选择模板下载操作模式更新并新增导入说明:1.仅支持").nth(5).click()
        
        logger.info("verify_import_button用例执行完成")
