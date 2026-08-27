import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool

class TestProductionOrderSplitHideRule(BaseTest):
    """
    用例名：productionorder_split_hide_rule
    用例ms的id：100103
    """

    def test_productionorder_split_hide_rule(self, page: Page, project_name: str):
        f"""测试生产订单拆分隐藏规则
        用例名：productionorder_split_hide_rule
        用例ms的id：100103
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行测试用例：productionorder_split_hide_rule")
        logger.info(f"用例ms ID：100103")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法登录系统
        logger.info("登录系统")
        self.login(page, project_name)
        
        # 进入生产订单页面
        logger.info("导航到生产订单页面")
        page.get_by_role("listitem", name="生产计划").click()
        page.get_by_text("生产订单").click()

        # 不选择订单，点击拆分按钮，按钮禁用
        logger.info("不选择订单，点击拆分按钮，按钮禁用")
        view_button = page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("button", name="拆分")
        Tool.assert_button_disabled(view_button, "拆分按钮")
        
        # 选择多条订单，点击拆分按钮，按钮禁用
        logger.info("选择多条订单，点击拆分按钮，按钮禁用")
        order_iframe = page.locator("iframe[name=\"ProductionOrders\"]").content_frame
        order_iframe.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        order_iframe.get_by_role("row").nth(2).get_by_label("", exact=True).check()
        view_button = page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("button", name="拆分")
        Tool.assert_button_disabled(view_button, "拆分按钮")
        
        logger.info("测试用例步骤执行完成")