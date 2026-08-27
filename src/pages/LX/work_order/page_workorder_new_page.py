from playwright.sync_api import Page
from src.data.LX.work_order.data_workorder_new_page import *
from src.common.logger import logger


class PageWorkorderNewPage:
    def __init__(self, page: Page):
        self.page = page
        # 元素定位器（集中管理，页面变更只需修改此处）
        self.production_management_menu = page.get_by_role("listitem", name="生产管理")
        self.workorder_submenu = page.get_by_text("生产工单")
        self.workorder_iframe_locator = "iframe[name=\"WorkOrder\"]"
        self.add_button_in_iframe = "新 增"
    
    def navigate_to_workorder_page(self):
        """导航到生产工单页面"""
        logger.info("进入生产工单页面")
        self.production_management_menu.click()
        self.workorder_submenu.click()
        # 等待主页面和iframe加载稳定
        self.page.wait_for_load_state('networkidle')
        self.page.wait_for_selector(self.workorder_iframe_locator, state="attached")
    
    def get_workorder_iframe(self):
        """获取生产工单页面的iframe"""
        iframe = self.page.frame(name="WorkOrder")
        if not iframe:
            raise Exception("无法找到WorkOrder iframe")
        return iframe
    
    def click_add_button_and_get_popup(self):
        """点击生产工单新增按钮并获取弹窗"""
        logger.info("点击生产工单新增按钮")
        iframe = self.get_workorder_iframe()
        # 使用expect_popup捕获弹窗
        with self.page.expect_popup() as page1_info:
            iframe.get_by_role("button", name=self.add_button_in_iframe).click()
        popup_page = page1_info.value
        # 等待弹窗加载稳定
        popup_page.wait_for_load_state('networkidle')
        return popup_page
    
    def close_popup(self, popup_page):
        """关闭新增弹窗"""
        logger.info("关闭生产工单新增弹窗")
        if not popup_page.is_closed():
            popup_page.close()