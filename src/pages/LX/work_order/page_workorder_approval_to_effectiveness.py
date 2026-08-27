from playwright.sync_api import Page
from src.data.LX.work_order.data_workorder_approval_to_effectiveness import WorkorderApprovalToEffectivenessData
from src.common.logger import logger


class WorkorderApprovalToEffectivenessPage:
    def __init__(self, page: Page):
        self.page = page
        # 主页面导航元素
        self.production_management = page.get_by_role("listitem", name="生产管理")
        self.production_workorder = page.get_by_text("生产工单")
        # 主界面iframe名称
        self.main_iframe_name = "WorkOrder"
    
    def navigate_to_workorder_page(self):
        """导航到生产工单页面"""
        logger.info("导航到生产管理菜单...")
        self.production_management.click()
        logger.info("导航到生产工单页面...")
        self.production_workorder.click()
        self.page.wait_for_load_state('networkidle')
    
    def get_main_iframe(self):
        """获取生产工单主界面iframe"""
        iframe = self.page.frame(self.main_iframe_name)
        if not iframe:
            raise Exception(f"无法找到 {self.main_iframe_name} iframe")
        return iframe
    
    def click_add_button_get_popup(self, main_iframe):
        """点击新增按钮并获取弹出的新增工单页面"""
        logger.info("点击新增按钮，等待弹窗...")
        add_button = main_iframe.get_by_role("button", name="新 增")
        with self.page.expect_popup() as popup_info:
            add_button.click()
        add_popup = popup_info.value
        add_popup.wait_for_load_state('networkidle')
        return add_popup
    
    def fill_add_workorder_form_and_copy_no(self, add_popup, data):
        """填写新增工单表单并复制工单号"""
        # 填写工单号
        logger.info("填写工单号...")
        wo_no_input = add_popup.get_by_role("textbox", name="* 工单号")
        wo_no_input.click()
        wo_no_input.fill(data["workorder_no"])
        
        # 选择物料
        logger.info("选择物料...")
        material_selector = add_popup.locator("svg").nth(4)
        material_selector.click()
        add_popup.get_by_role("row").filter(has_text=data["material_row_name"]).get_by_label("", exact=True).check()
        add_popup.get_by_role("button", name="确 定").click()
        
        # 选择相关工单配置项
        logger.info("选择相关工单配置项...")
        config_selector = add_popup.locator("div:nth-child(5) > div > .ant-row > .ant-col.ant-form-item-control > .ant-form-item-control-input > .ant-form-item-control-input-content > .ant-select > .ant-select-arrow > div > .anticon.anticon-search > svg")
        config_selector.click()
        add_popup.get_by_label("", exact=True).check()
        add_popup.get_by_role("button", name="确 定").click()
        
        # 填写计划产量
        logger.info("填写计划产量...")
        plan_qty_input = add_popup.get_by_role("spinbutton", name="* 计划产量")
        plan_qty_input.click()
        plan_qty_input.fill(data["plan_qty"])
        
        # 复制工单号
        logger.info("复制工单号...")
        wo_no_input.click()
        wo_no_input.press("ControlOrMeta+A")
        wo_no_input.press("ControlOrMeta+C")
        
        return data["workorder_no"]
    
    def submit_approval_and_close_popup(self, add_popup):
        """提交审批并关闭新增弹窗"""
        logger.info("点击审批按钮...")
        add_popup.get_by_role("button", name="审 批").click()
        add_popup.close()
        self.page.wait_for_load_state('networkidle')
    
    def query_workorder(self, main_iframe, wo_no, status):
        """查询指定工单号和状态的工单"""
        # 粘贴工单号
        logger.info("粘贴工单号至查询框...")
        wo_no_query = main_iframe.get_by_role("textbox", name="工单号 :")
        wo_no_query.click()
        wo_no_query.press("ControlOrMeta+V")
        
        # 选择工单状态
        logger.info("选择工单状态...")
        status_combobox = main_iframe.get_by_role("combobox", name="工单状态 :")
        status_combobox.click()
        main_iframe.get_by_text(status).nth(1).click()
        main_iframe.locator("form").get_by_text("工单状态").click()
        
        # 点击查询
        logger.info("点击查询按钮...")
        main_iframe.get_by_role("button", name="查询").click()
        self.page.wait_for_load_state('networkidle')
    
    def check_and_effect_workorder(self, main_iframe):
        """勾选查询到的工单并生效"""
        logger.info("勾选工单并生效...")
        main_iframe.get_by_label("", exact=True).check()
        main_iframe.get_by_role("button", name="生 效").click()
        self.page.wait_for_load_state('networkidle')
    
    def check_and_issue_workorder(self, main_iframe):
        """再次勾选查询到的工单并下发"""
        logger.info("勾选工单并下发...")
        main_iframe.get_by_label("", exact=True).check()
        main_iframe.get_by_role("button", name="下 发").click()
        self.page.wait_for_load_state('networkidle')