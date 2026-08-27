import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.pages.LX.production_order.page_productionorder_edit_success import ProductionorderEditSuccessPage
from src.data.LX.production_order.data_productionorder_edit_success import ProductionOrderEditData

class TestProductionorderEditSuccess(BaseTest):
    """
    用例名：productionorder_edit_success
    用例ms的id：100100
    """

    def test_productionorder_edit_success(self, page: Page, project_name: str):
        f"""测试生产订单编辑成功功能
        用例名：productionorder_edit_success
        用例ms的id：100100
        项目名：{project_name}
        """
        logger.info("=" * 60)
        logger.info(f"开始执行productionorder_edit_success")
        logger.info(f"用例ms的id：100100")
        logger.info("=" * 60)
        try:
            # 公用登录
            self.login(page, project_name)
            
            # 初始化页面对象
            po_page = ProductionorderEditSuccessPage(page)
            
            # 导航到生产订单页面
            po_page.navigate_to_production_order_page()
            
            # 获取主iframe
            po_frame = po_page.get_po_iframe()
            
            # 创建新生产订单
            po_page.click_add_button()
            po_page.fill_order_number()
            po_page.select_original_production_line()
            po_page.select_original_material()
            po_page.fill_initial_plan_quantity()
            po_page.set_initial_plan_end_date()
            po_page.click_confirm_button()
            
            # 查询订单进入编辑
            po_page.search_and_enter_edit()
            
            # 修改订单信息
            po_page.edit_production_line()
            po_page.edit_material()
            po_page.edit_plan_quantity()
            po_page.edit_plan_end_date()
            po_page.confirm_success()
            
            logger.info(f"productionorder_edit_success用例执行完成")
            
        except Exception as e:
            logger.error(f"测试执行失败: {str(e)}", exc_info=True)
            raise