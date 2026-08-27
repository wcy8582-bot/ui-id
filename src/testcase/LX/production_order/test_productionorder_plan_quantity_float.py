import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.pages.LX.production_order.page_productionorder_plan_quantity_float import ProductionorderPlanQuantityFloatPage
from src.data.LX.production_order.data_productionorder_plan_quantity_float import ProductionOrderData


class TestProductionorderPlanQuantityFloat(BaseTest):
    """
    用例名：productionorder_plan_quantity_float
    用例ms的id：100081
    """

    def test_productionorder_plan_quantity_float(self, page: Page, project_name: str):
        f"""测试生产订单计划数量浮点数验证功能
        用例名：productionorder_plan_quantity_float
        用例ms的id：{ProductionOrderData['ms_id']}
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        try:
            logger.info("=" * 60)
            logger.info(f"开始执行productionorder_plan_quantity_float")
            logger.info(f"用例ms的id：{ProductionOrderData['ms_id']}")
            logger.info("=" * 60)
            
            # 使用公用登录方法
            self.login(page, project_name)
            
            # 初始化页面对象
            production_page = ProductionorderPlanQuantityFloatPage(page)
            
            # 导航到生产订单页面
            production_page.navigate_to_production_order_page()
            
            # 获取生产订单iframe的内容框架
            production_iframe = production_page.get_production_iframe()
            
            # 点击新增按钮
            production_page.click_add_button(production_iframe)
            
            # 输入计划数量
            production_page.fill_plan_quantity(production_iframe, ProductionOrderData['test_input_quantity'])
            
            # 验证计划数量自动保留6位小数
            logger.info(f"验证计划数量自动保留6位小数")
            production_page.verify_plan_quantity_value(production_iframe)
            
            logger.info("生产订单计划数量浮点数验证功能测试执行完成！")
            
        except Exception as e:
            logger.error(f"测试执行失败: {str(e)}")
            raise