import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestImportMode(BaseTest):
    """
    用例名：import_mode
    用例ms的id：101313
    """

    def test_import_mode(self, page: Page, project_name: str):
        f"""测试物料清单导入功能
        用例名：import_mode
        用例ms的id：101313
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：import_mode")
        logger.info(f"用例ms的id：101313")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入基础资料-物料清单页面
        logger.info("进入基础资料模块，打开物料清单页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("物料清单").click()
        
        # 点击导入按钮，验证弹窗元素可见
        logger.info("点击导入按钮，验证导入弹窗元素")
        content_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        expect(content_frame.get_by_role("button", name="import 导入")).to_be_visible()
        content_frame.get_by_role("button", name="import 导入").click()
        expect(content_frame.locator("div").filter(has_text=re.compile(r"^导入$")).first).to_be_visible()
        expect(content_frame.get_by_text("文件选择模板下载操作模式更新并新增导入说明:1.仅支持")).to_be_visible()
        
        logger.info(f"用例import_mode执行完成")