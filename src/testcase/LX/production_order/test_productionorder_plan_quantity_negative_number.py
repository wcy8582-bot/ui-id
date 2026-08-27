import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestProductionOrderPlanQuantityNegative(BaseTest):
    """
    用例名：productionorder_plan_quantity_negative_number
    用例ms的id：100097
    """

    def test_productionorder_plan_quantity_negative_number(self, page: Page, project_name: str):
        f"""测试生产订单计划数量负数校验
        用例名：productionorder_plan_quantity_negative_number
        用例ms的id：100097
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行测试用例：productionorder_plan_quantity_negative_number")
        logger.info(f"用例ms的id：100097")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产订单菜单
        logger.info("进入生产计划->生产订单页面")
        page.get_by_role("listitem", name="生产计划").click()
        page.get_by_text("生产订单").click()
        
        # 获取生产订单iframe，点击新增按钮
        po_iframe = page.locator("iframe[name=\"ProductionOrders\"]").content_frame
        logger.info("点击新增生产订单按钮")
        po_iframe.get_by_role("button", name="新 增").click()
        
        # 计划数量输入框输入负数-1
        logger.info("在计划数量输入框填入负数-1")
        po_iframe.get_by_role("spinbutton", name="* 计划数量").click()
        po_iframe.get_by_role("spinbutton", name="* 计划数量").fill("-1")
        
        # 提交新增，校验错误提示
        logger.info("提交新增，校验错误提示信息")
        po_iframe.get_by_text("新增生产订单").click()
        expect(po_iframe.locator("#planNum_help")).to_contain_text("计划数量不能小于0")
        
        logger.info(f"测试用例productionorder_plan_quantity_negative_number执行完成")