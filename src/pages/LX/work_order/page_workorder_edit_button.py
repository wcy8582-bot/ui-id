from playwright.sync_api import Page
from src.data.LX.work_order.data_workorder_edit_button import WorkorderEditButtonData
from src.common.logger import logger


class WorkorderEditButtonPage:
    def __init__(self, page: Page):
        self.page = page
        # 主页面导航元素定位器
        self.production_management = page.get_by_role("listitem", name=WorkorderEditButtonData["production_management_text"])
        self.production_workorder = page.get_by_text(WorkorderEditButtonData["production_workorder_text"])
        # iframe名称
        self.main_iframe_name = WorkorderEditButtonData["main_iframe_name"]
        # 弹窗处理相关
        self.popup_timeout = WorkorderEditButtonData["popup_timeout"]
        
    def navigate_to_workorder_page(self):
        """导航到生产工单页面"""
        logger.info("进入生产工单页面")
        self.production_management.click()
        self.production_workorder.click()
        self.page.wait_for_load_state('networkidle')
        
    def get_main_iframe(self):
        """获取生产工单主iframe"""
        logger.info("获取生产工单主iframe")
        iframe = self.page.frame(self.main_iframe_name)
        if not iframe:
            raise Exception(f"无法找到名称为 {self.main_iframe_name} 的iframe")
        return iframe
        
    def click_add_button(self, iframe):
        """点击新增按钮并等待弹窗"""
        logger.info("点击新增按钮打开新增工单弹窗")
        with self.page.expect_popup(timeout=self.popup_timeout) as page_info:
            iframe.get_by_role("button", name=WorkorderEditButtonData["add_button_text"]).click()
        return page_info.value
        
    def fill_add_workorder_form(self, modal_page):
        """填写新增工单表单"""
        logger.info("填写新增工单信息")
        # 填写工单号
        modal_page.get_by_role("textbox", name=WorkorderEditButtonData["workorder_no_label"]).fill(WorkorderEditButtonData["workorder_no"])
        # 选择物料
        modal_page.locator("svg").nth(4).click()
        modal_page.get_by_role("row", name=WorkorderEditButtonData["material_row_text"]).get_by_label("", exact=True).check()
        modal_page.get_by_role("button", name=WorkorderEditButtonData["confirm_button_text"]).click()
        # 填写计划产量
        modal_page.get_by_role("spinbutton", name=WorkorderEditButtonData["plan_qty_label"]).fill(WorkorderEditButtonData["plan_qty"])
        # 选择工序/人员（按原代码操作）
        modal_page.locator("div:nth-child(5) > div > .ant-row > .ant-col.ant-form-item-control > .ant-form-item-control-input > .ant-form-item-control-input-content > .ant-select > .ant-select-arrow > div > .anticon.anticon-search > svg").click()
        modal_page.get_by_label("", exact=True).check()
        modal_page.get_by_role("button", name=WorkorderEditButtonData["confirm_button_text"]).click()
        
    def save_and_close_modal(self, modal_page):
        """保存表单并关闭弹窗"""
        logger.info("保存新增工单并关闭弹窗")
        modal_page.get_by_role("button", name=WorkorderEditButtonData["save_button_text"]).click()
        self.close_modal(modal_page)
        
    def search_workorder(self, iframe):
        """根据工单号查询工单"""
        logger.info("查询已保存的生产工单")
        iframe.get_by_role("textbox", name=WorkorderEditButtonData["search_workorder_no_label"]).fill(WorkorderEditButtonData["workorder_no"])
        iframe.get_by_role("button", name=WorkorderEditButtonData["search_button_text"]).click()
        self.page.wait_for_load_state('networkidle')
        
    def click_edit_button(self, iframe):
        """选中第一个工单并点击编辑按钮等待弹窗"""
        logger.info("选中工单并点击编辑按钮打开编辑弹窗")
        iframe.get_by_label("", exact=True).check()
        with self.page.expect_popup(timeout=self.popup_timeout) as page_info:
            iframe.get_by_role("button", name=WorkorderEditButtonData["edit_button_text"]).click()
        return page_info.value
        
    def close_modal(self, modal_page):
        """关闭弹窗"""
        modal_page.close()