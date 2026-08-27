from playwright.sync_api import Page
from src.data.LX.work_order.data_workorder_edit_to_effectiveness import *
from src.common.logger import logger


class WorkorderEditToEffectivenessPage:
    def __init__(self, page: Page):
        self.page = page
        # 主页面元素定位器
        self.production_management_menu = page.get_by_role("listitem", name=MainPageData["production_management"])
        self.work_order_submenu = page.get_by_text(MainPageData["work_order"])
        # iframe名称
        self.iframe_name = WorkOrderData["iframe_name"]

    def navigate_to_workorder_page(self):
        """导航到生产工单页面"""
        logger.info("进入生产工单页面")
        self.production_management_menu.click()
        self.work_order_submenu.click()
        self.page.wait_for_load_state('networkidle')

    def get_workorder_iframe(self):
        """获取生产工单iframe"""
        logger.info("获取生产工单iframe")
        iframe = self.page.frame(self.iframe_name)
        if not iframe:
            raise Exception(f"无法找到名称为 {self.iframe_name} 的iframe")
        return iframe

    def click_add_button(self, iframe):
        """点击新增按钮，返回新增弹窗页面对象"""
        logger.info("点击新增按钮，弹出新增工单窗口")
        with self.page.expect_popup() as popup_info:
            iframe.get_by_role("button", name=WorkOrderData["btn_add"]).click()
        popup_page = popup_info.value
        popup_page.wait_for_load_state('networkidle')
        return popup_page

    def fill_add_workorder_info(self, popup_page):
        """填写新增工单信息，返回复制的工单号"""
        # 填写工单号
        logger.info("填写工单号")
        wo_no_input = popup_page.get_by_role("textbox", name=AddModalData["wo_no_label"])
        wo_no_input.fill(AddModalData["wo_no"])
        
        # 选择物料
        logger.info("选择物料")
        popup_page.locator("svg").nth(4).click()
        popup_page.get_by_role("row").filter(has_text=AddModalData["material_row_name"]).get_by_label("", exact=True).check()
        popup_page.get_by_role("button", name=WorkOrderData["btn_confirm"]).click()
        
        # 填写计划产量
        logger.info("填写计划产量")
        plan_qty_input = popup_page.get_by_role("spinbutton", name=AddModalData["plan_qty_label"])
        plan_qty_input.fill(AddModalData["plan_qty"])
        
        # 选择其他必填项
        logger.info("选择其他必填项")
        popup_page.locator("div:nth-child(5) > div > .ant-row > .ant-col.ant-form-item-control > .ant-form-item-control-input > .ant-form-item-control-input-content > .ant-select > .ant-select-arrow > div > .anticon.anticon-search > svg").click()
        popup_page.get_by_label("", exact=True).check()
        popup_page.get_by_role("button", name=WorkOrderData["btn_confirm"]).click()
        
        # 复制工单号
        logger.info("复制工单号")
        wo_no_input.press("ControlOrMeta+A")
        wo_no_input.press("ControlOrMeta+C")
        
        return AddModalData["wo_no"]

    def save_and_close_add_modal(self, popup_page):
        """保存新增工单并关闭弹窗"""
        logger.info("保存新增工单，关闭窗口")
        popup_page.get_by_role("button", name=WorkOrderData["btn_save"]).click()
        popup_page.wait_for_load_state('networkidle')
        popup_page.close()

    def paste_and_query(self, iframe, copied_wo_no):
        """粘贴工单号到查询框并查询"""
        logger.info("粘贴工单号到查询框并查询")
        query_input = iframe.get_by_role("textbox", name=WorkOrderData["query_wo_no_label"])
        # 先清空输入框避免旧值干扰，再粘贴（模拟手动粘贴）
        query_input.fill("")
        query_input.press("ControlOrMeta+V")
        iframe.get_by_role("button", name=WorkOrderData["btn_query"]).click()
        self.page.wait_for_load_state('networkidle')

    def select_and_effect(self, iframe):
        """选中工单并生效"""
        logger.info("选中工单并生效")
        iframe.get_by_label("", exact=True).check()
        iframe.get_by_role("button", name=WorkOrderData["btn_effect"]).click()
        self.page.wait_for_load_state('networkidle')

    def select_and_abandon_then_cancel(self, iframe):
        """选中工单并废弃、取消"""
        logger.info("选中工单并废弃、取消")
        iframe.get_by_label("", exact=True).check()
        iframe.get_by_role("button", name=WorkOrderData["btn_abandon"]).click()
        iframe.get_by_role("button", name=WorkOrderData["btn_cancel"]).click()
        self.page.wait_for_load_state('networkidle')