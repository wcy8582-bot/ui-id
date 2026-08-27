import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestCreateButton(BaseTest):
    """
    用例名：test_create_button
    用例ms的id：101190
    """

    def test_create_button(self, page: Page, project_name: str):
        f"""测试产品档案新增创建按钮功能
        用例名：create_button
        用例ms的id：101190
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：test_create_button")
        logger.info(f"用例ms的id：101190")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法
        logger.info("完成系统登录")
        self.login(page, project_name)
        
        # 导航到产品档案页面
        logger.info("进入产品档案模块")
        page.locator("div").filter(has_text=re.compile(r"^基础资料$")).nth(2).click()
        page.get_by_text("产品档案").click()
        
        # 获取内容iframe，简化后续定位
        product_iframe = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 点击新增按钮打开创建弹窗
        logger.info("点击新增按钮打开创建产品弹窗")
        product_iframe.get_by_role("button", name="plus-circle 新增").click()
        
        # 验证弹窗内容正确性
        logger.info("验证创建弹窗包含产品图片字段")
        expect(product_iframe.get_by_label("创建产品").locator("form")).to_contain_text("产品图片")
        
        # 关闭创建弹窗
        logger.info("关闭创建产品弹窗")
        product_iframe.get_by_role("button", name="Close").click()
        
        logger.info("create_button用例执行完成")