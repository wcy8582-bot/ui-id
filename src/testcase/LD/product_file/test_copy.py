import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestCopyProduct(BaseTest):
    """
    用例名：copy
    用例ms的id：100947
    """

    def test_copy(self, page: Page, project_name: str):
        f"""测试复制产品档案功能
        用例名：copy
        用例ms的id：100947
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：copy")
        logger.info(f"用例ms的id：100947")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入产品档案菜单
        logger.info("进入产品档案页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("产品档案").click()

        # 获取目标iframe内容帧，简化后续代码调用
        product_iframe = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame

        # 验证操作列及复制按钮可见
        logger.info("验证操作列和复制按钮可用性")
        product_iframe.get_by_role("columnheader", name="操作").click()
        expect(product_iframe.get_by_role("cell").filter(has_text="编辑复制删除").first).to_be_visible()
        expect(product_iframe.get_by_text("复制").first).to_be_visible()

        # 点击复制按钮
        logger.info("点击第一个产品的复制按钮")
        product_iframe.get_by_text("复制").nth(1).click()

        # 保存复制的产品
        logger.info("点击保存复制的产品信息")
        product_iframe.get_by_role("button", name="保 存").click()


        logger.info("用例copy执行完成")