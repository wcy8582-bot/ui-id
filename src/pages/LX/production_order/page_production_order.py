from playwright.sync_api import Page
from src.common.logger import logger
from src.common.data_generator import DataGenerator


class PageProductionOrder:
    def __init__(self, page: Page):
        self.page = page
        self.production_iframe_name = "ProductionOrders"

    def navigate_to_production_order_page(self):
        """导航到生产订单页面"""
        logger.info("进入生产订单页面")
        self.page.get_by_role("listitem", name="生产计划").click()
        self.page.get_by_role("listitem", name="生产订单").click()
        self.page.get_by_text("生产订单").click()
        self.page.wait_for_load_state('networkidle')

    def get_production_iframe(self):
        """获取生产订单页面的iframe"""
        iframe = self.page.frame(name=self.production_iframe_name)
        if not iframe:
            raise Exception(f"无法找到{self.production_iframe_name} iframe")
        return iframe

    def click_add_button(self):
        """点击新增按钮"""
        logger.info("点击新增按钮")
        iframe = self.get_production_iframe()
        iframe.get_by_role("button", name="新 增").click()
        self.page.wait_for_timeout(2000)

    def fill_order_no(self, order_no: str):
        """填写生产订单号"""
        logger.info(f"填写生产订单号: {order_no}")
        iframe = self.get_production_iframe()
        iframe.get_by_role("textbox", name="请输入").fill(order_no)

    def click_material_refer_button(self, index: int = 6):
        """点击物料参照按钮"""
        logger.info("点击物料参照按钮")
        iframe = self.get_production_iframe()
        refer_button = iframe.locator("button.ant-btn-icon-only").nth(index)
        refer_button.wait_for(state="visible", timeout=20000)
        refer_button.evaluate("el => el.click()")

    def select_first_row_in_refer_popup(self):
        """在参照弹窗中勾选第一行"""
        logger.info("勾选参照弹窗第一行")
        iframe = self.get_production_iframe()
        refer_frame = iframe.locator("iframe").content_frame
        refer_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()

    def click_refer_confirm_button(self, refer_name: str):
        """点击参照弹窗的确定按钮"""
        logger.info(f"点击{refer_name}确定按钮")
        iframe = self.get_production_iframe()
        iframe.get_by_label(refer_name).get_by_role("button", name="确 定").click()

    def fill_plan_quantity(self, quantity: str):
        """填写计划数量"""
        logger.info(f"填写计划数量: {quantity}")
        iframe = self.get_production_iframe()
        iframe.get_by_role("spinbutton", name="* 计划数量").click()
        iframe.get_by_role("spinbutton", name="* 计划数量").fill(quantity)

    def fill_plan_date(self):
        """填写计划日期"""
        logger.info("填写计划日期")
        iframe = self.get_production_iframe()
        iframe.get_by_role("textbox", name="计划结束日期").click()
        iframe.get_by_role("textbox", name="计划结束日期").fill(DataGenerator().get_random_end_date())
        iframe.get_by_text("新增生产订单").click()

    def fill_remark(self, remark: str):
        """填写备注"""
        logger.info(f"填写备注: {remark}")
        iframe = self.get_production_iframe()
        iframe.get_by_role("textbox", name="备注").click()
        iframe.get_by_role("textbox", name="备注").fill(remark)

    def click_confirm_button(self):
        """点击确认按钮"""
        logger.info("点击确认按钮")
        iframe = self.get_production_iframe()
        iframe.get_by_role("button", name="确 定").click()