import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool



class TestProductionOrderEditTwoOrder(BaseTest):
    """
    用例名：productionorder_edit_two_order
    用例ms的id：100086
    """

    def test_productionorder_edit_two_order(self, page: Page, project_name: str):
        f"""测试生产订单勾选多个订单编辑功能
        用例名：productionorder_edit_two_order
        用例ms的id：100086
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：productionorder_edit_two_order")
        logger.info(f"用例ms ID：100086")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法登录系统
        logger.info("调用公用登录方法登录系统")
        self.login(page, project_name)
        
        # 进入生产订单页面
        logger.info("导航到生产订单页面")
        page.get_by_role("listitem", name="生产计划").click()
        page.get_by_text("生产订单").click()
        
        # 勾选目标两个生产订单
        logger.info("勾选列表中两个目标生产订单")
        order_iframe = page.locator("iframe[name=\"ProductionOrders\"]").content_frame
        order_iframe.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        order_iframe.get_by_role("row").nth(2).get_by_label("", exact=True).check()
        
        # 点击生产订单iframe内的编辑按钮
        logger.info("点击编辑按钮")
        view_button = page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("button", name="编 辑")
        Tool.assert_button_disabled(view_button, "编辑按钮")
        logger.info("测试用例productionorder_edit_hide执行完成")