import re
from playwright.sync_api import Page, expect
from src.data.LX.production_order.data_productionorder_plan_quantity_float import ProductionOrderData
from src.common.logger import logger


class ProductionorderPlanQuantityFloatPage:
    def __init__(self, page: Page):
        self.page = page
        # 集中定义元素定位器
        self.production_plan_menu = page.get_by_role("listitem", name=ProductionOrderData['menu_production_plan'])
        self.production_order_submenu = page.get_by_text(ProductionOrderData['menu_production_order'])
    
    def navigate_to_production_order_page(self):
        """导航到生产订单页面"""
        logger.info("进入生产订单页面")
        self.production_plan_menu.click()
        self.production_order_submenu.click()
        # 等待页面加载完成
        self.page.wait_for_load_state('networkidle')
    
    def get_production_iframe(self):
        """获取生产订单iframe的内容框架"""
        iframe = self.page.frame(ProductionOrderData['iframe_name'])
        if not iframe:
            raise Exception(f"无法找到名称为{ProductionOrderData['iframe_name']}的iframe")
        return iframe
    
    def click_add_button(self, iframe):
        """点击新增生产订单按钮"""
        logger.info("点击新增生产订单按钮")
        add_button = iframe.get_by_role("button", name=ProductionOrderData['btn_add'])
        add_button.click()
        # 等待新增操作的响应加载（可根据实际情况调整）
        self.page.wait_for_load_state('networkidle')
    
    def fill_plan_quantity(self, iframe, quantity):
        """输入计划数量"""
        logger.info(f"输入计划数量浮点数{quantity}")
        quantity_spinner = iframe.get_by_role("spinbutton", name=ProductionOrderData['spinner_plan_quantity_name'])
        quantity_spinner.fill(quantity)
        iframe.get_by_text("新增生产订单").click()
        # 等待输入响应（可根据实际情况调整）
        self.page.wait_for_load_state('networkidle')
    
    def verify_plan_quantity_value(self, iframe):
        """验证计划数量的实际值为六位小数"""
        quantity_spinner = iframe.get_by_role("spinbutton", name=ProductionOrderData['spinner_plan_quantity_name'])
        
        # 验证是否为六位小数
        actual_value = quantity_spinner.get_attribute("value")
        if actual_value:
            # 检查是否为六位小数格式（必须有小数点且后面有恰好六位数字）
            decimal_pattern = r'^\d+\.\d{6}$'
            is_six_decimal = bool(re.match(decimal_pattern, actual_value))
            assert is_six_decimal, f"计划数量不是六位小数格式，实际值: {actual_value}"
            logger.info(f"验证通过：计划数量为六位小数格式: {actual_value}")
        else:
            assert False, "无法获取计划数量的值"