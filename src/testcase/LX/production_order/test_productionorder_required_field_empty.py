import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestProductionOrderRequiredFieldEmpty(BaseTest):
    """
    用例名：productionorder_required_field_empty
    用例ms的id：100077
    """

    def test_productionorder_required_field_empty(self, page: Page, project_name: str):
        f"""测试生产订单必填项为空的功能
        用例名：productionorder_required_field_empty
        用例ms的id：100077
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行productionorder_required_field_empty")
        logger.info(f"用例ms的id：100099")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产订单页面
        logger.info("进入生产订单页面")
        page.get_by_role("listitem", name="生产计划").click()
        page.get_by_text("生产订单").click()
        
        # 点击新增、确定按钮并验证必填项提示
        logger.info("点击生产订单新增按钮")
        page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("button", name="新 增").click()
        logger.info("点击生产订单新增页面确定按钮")
        page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("button", name="确 定").click()
        logger.info("验证生产订单号必填项提示")
        expect(page.locator("iframe[name=\"ProductionOrders\"]").content_frame.locator("#orderNo_help")).to_contain_text("请输入生产订单号")
        page.close()