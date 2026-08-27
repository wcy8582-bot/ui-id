import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestViewTableBody(BaseTest):
    """
    用例名：view_table_body
    用例ms的id：101210
    """

    def test_view_table_body(self, page: Page, project_name: str):
        f"""测试查看产品档案表格功能
        用例名：view_table_body
        用例ms的id：101210
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：view_table_body")
        logger.info(f"用例ms的id：101210")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法
        self.login(page, project_name)


        # 进入产品档案页面
        logger.info("点击基础资料菜单")
        page.get_by_text("基础资料").click()
        logger.info("点击产品档案菜单")
        page.get_by_text("产品档案").click()
        
        # 获取产品档案iframe内容框架，简化重复定位
        iframe_content = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        logger.info("验证表格表头包含所有预期字段")
        expect(iframe_content.locator("thead")).to_contain_text("序号")
        expect(iframe_content.locator("thead")).to_contain_text("产品编码")
        expect(iframe_content.locator("thead")).to_contain_text("产品名称")
        expect(iframe_content.locator("thead")).to_contain_text("产品规格")
        expect(iframe_content.locator("thead")).to_contain_text("产品图片")
        expect(iframe_content.locator("thead")).to_contain_text("产品型号")
        expect(iframe_content.locator("thead")).to_contain_text("操作")
        
        logger.info("验证第一行操作按钮可见性")
        expect(iframe_content.get_by_text("编辑").first).to_be_visible()
        expect(iframe_content.get_by_text("复制").first).to_be_visible()
        expect(iframe_content.get_by_text("删除").first).to_be_visible()
        
        logger.info("验证右上角退出按钮可见性")
        expect(page.get_by_title("退出")).to_be_visible()
        
        logger.info(f"用例view_table_body执行完成")