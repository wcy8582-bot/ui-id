import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.pages.LX.production_order.page_production_order import PageProductionOrder
from src.data.LX.production_order.data_production_order import *


class TestProductionOrder(BaseTest):
    """
    用例名：production_order
    用例ms的id：100084
    """

    def test_production_order(self, page: Page, project_name: str):
        """测试生产订单新增功能
        用例名：production_order
        用例ms的id：100084
        项目名：LX

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        try:
            logger.info("=" * 60)
            logger.info(f"开始执行生产订单新增测试")
            logger.info(f"用例ms的id：100084")
            logger.info("=" * 60)

            self.login(page, project_name)
            logger.info("登录成功")

            production_order_page = PageProductionOrder(page)

            production_order_page.navigate_to_production_order_page()

            production_order_page.click_add_button()

            production_order_page.fill_order_no(ProductionOrderData["order_no"])

            production_order_page.click_material_refer_button()
            production_order_page.select_first_row_in_refer_popup()
            production_order_page.click_refer_confirm_button("物料参照")

            production_order_page.click_material_refer_button(5)
            production_order_page.select_first_row_in_refer_popup()
            production_order_page.click_refer_confirm_button("车间/产线参照")

            production_order_page.fill_plan_quantity(ProductionOrderData["plan_quantity"])

            production_order_page.fill_plan_date()

            production_order_page.fill_remark(ProductionOrderData["remark"])

            production_order_page.click_confirm_button()

            logger.info("生产订单新增测试执行完成！")

        except Exception as e:
            logger.error(f"测试执行失败: {str(e)}")
            raise
        finally:
            if not page.is_closed():
                page.close()