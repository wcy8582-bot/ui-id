import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyEditPageData(BaseTest):
    """
    用例名：verify_editpage_data
    用例ms的id：101212
    """

    def test_verify_editpage_data(self, page: Page, project_name: str):
        f"""测试物料清单编辑页面操作
        用例名：verify_editpage_data
        用例ms的id：101212
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_editpage_data")
        logger.info(f"用例ms的id：101212")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法登录系统
        logger.info("执行系统登录")
        self.login(page, project_name)
        

        
        # 导航到物料清单菜单
        logger.info("进入基础资料->物料清单页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("物料清单").click()
        
        # 编辑后取消操作
        logger.info("点击首个编辑按钮，随后点击取消")
        content_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        content_frame.get_by_text("编辑").first.click()
        content_frame.get_by_role("button", name="取 消").click()
        
        logger.info(f"用例verify_editpage_data执行完成")