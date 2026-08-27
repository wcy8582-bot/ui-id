from playwright.sync_api import Page
from src.data.LX.production_order.data_productionorder_edit_success import ProductionOrderEditData
from src.common.logger import logger
import re
import pytest
from playwright.sync_api import Page, expect

class ProductionorderEditSuccessPage:
    def __init__(self, page: Page):
        self.page = page
        # 页面基础元素定位
        self.production_iframe_name = "ProductionOrders"

    def get_production_iframe(self):
        """获取生产订单页面的iframe"""
        iframe = self.page.frame(name=self.production_iframe_name)
        if not iframe:
            raise Exception(f"无法找到{self.production_iframe_name} iframe")
        return iframe

    def navigate_to_production_order_page(self):
        """导航到生产订单页面"""
        logger.info("进入生产订单页面")
        self.page.get_by_role("listitem", name="生产计划").click()
        self.page.get_by_role("listitem", name="生产订单").click()
        self.page.get_by_text("生产订单").click()
        self.page.wait_for_load_state('networkidle')

    def get_po_iframe(self):
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

    def fill_order_number(self):
        """填写生产订单号"""
        logger.info(f"填写生产订单号")
        iframe = self.get_production_iframe()
        iframe.get_by_role("textbox", name="请输入").fill(ProductionOrderEditData["order_number"])

    def select_original_production_line(self):
        """点击产线参照按钮"""
        logger.info("点击产线参照按钮")
        iframe = self.get_production_iframe()
        refer_button = iframe.locator("button.ant-btn-icon-only").nth(5)
        refer_button.wait_for(state="visible", timeout=20000)
        refer_button.evaluate("el => el.click()")
        refer_frame = iframe.locator("iframe").content_frame
        refer_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        logger.info(f"点击确定按钮")
        iframe.get_by_label("车间/产线参照").get_by_role("button", name="确 定").click()

    def select_original_material(self):
        logger.info("选择生产物料")
        iframe = self.get_production_iframe()
        refer_button = iframe.locator("button.ant-btn-icon-only").nth(6)
        refer_button.wait_for(state="visible", timeout=20000)
        refer_button.evaluate("el => el.click()")
        refer_frame = iframe.locator("iframe").content_frame
        refer_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        logger.info(f"点击确定按钮")
        iframe.get_by_label("物料参照").get_by_role("button", name="确 定").click()

    def fill_initial_plan_quantity(self):
        """输入初始计划生产数量"""
        logger.info(f"填写初始计划数量: {ProductionOrderEditData["initial_plan_quantity"]}")
        iframe = self.get_production_iframe()
        iframe.get_by_role("spinbutton", name="* 计划数量").click()
        iframe.get_by_role("spinbutton", name="* 计划数量").fill(ProductionOrderEditData["initial_plan_quantity"])

    def set_initial_plan_end_date(self):
        """设置初始计划结束日期"""
        logger.info("设置计划结束日期")
        iframe = self.get_production_iframe()
        iframe.locator("div:nth-child(2) > .ant-form-item > .ant-row > .ant-col.ant-form-item-control > .ant-form-item-control-input > .ant-form-item-control-input-content > .ant-picker > .ant-picker-input").click()
        iframe.get_by_role("button", name="下个月 (翻页下键)").click()
        iframe.get_by_text("1", exact=True).nth(2).click()

    def click_confirm_button(self):
        """点击确认按钮"""
        logger.info("点击确认按钮")
        self.page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("button", name="确 定").click()

    def search_and_enter_edit(self):
        """查询订单后进入编辑页面"""
        logger.info("查询订单后进入编辑")
        iframe = self.get_production_iframe()
        iframe.get_by_role("button", name=ProductionOrderEditData["query_button_name"]).click()
        order_row = iframe.get_by_role("row").nth(1)
        order_row.get_by_label("", exact=True).check()
        iframe.get_by_role("button", name=ProductionOrderEditData["edit_button_name"]).click()

    def edit_production_line(self):
        """修改产线信息"""
        logger.info("修改产线信息")
        iframe = self.get_production_iframe()
        refer_button = iframe.locator("button.ant-btn-icon-only").nth(5)
        refer_button.wait_for(state="visible", timeout=20000)
        refer_button.evaluate("el => el.click()")
        refer_frame = iframe.locator("iframe").content_frame
        refer_frame.get_by_role("row").nth(2).get_by_label("", exact=True).check()
        logger.info(f"点击确定按钮")
        iframe.get_by_label("车间/产线参照").get_by_role("button", name="确 定").click()

    def edit_material(self):
        """修改物料信息"""
        logger.info("修改物料信息")
        iframe = self.get_production_iframe()
        refer_button = iframe.locator("button.ant-btn-icon-only").nth(6)
        refer_button.wait_for(state="visible", timeout=20000)
        refer_button.evaluate("el => el.click()")
        refer_frame = iframe.locator("iframe").content_frame
        refer_frame.get_by_role("row").nth(2).get_by_label("", exact=True).check()
        logger.info(f"点击确定按钮")
        iframe.get_by_label("物料参照").get_by_role("button", name="确 定").click()

    def edit_plan_quantity(self):
        """修改计划生产数量"""
        logger.info("修改计划生产数量")
        iframe = self.get_production_iframe()
        iframe.get_by_role("spinbutton", name="* 计划数量").click()
        iframe.get_by_role("spinbutton", name="* 计划数量").fill(ProductionOrderEditData["edited_plan_quantity"])

    def edit_plan_end_date(self):
        """修改计划结束日期"""
        logger.info("修改计划结束日期")
        iframe = self.get_production_iframe()
        iframe.get_by_role("button", name=ProductionOrderEditData["close_button_name"]).nth(1).click()
        iframe.get_by_role("textbox", name="计划结束日期").click()
        iframe.get_by_text(ProductionOrderEditData["today_text"]).click()

    def confirm_success(self):
        """确认编辑成功"""
        logger.info("确认编辑成功")
        iframe = self.get_production_iframe()
        iframe.get_by_role("button", name="确 定").click()
        expect(iframe.locator("body")).to_contain_text("修改成功")
