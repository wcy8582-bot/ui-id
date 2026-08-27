from playwright.sync_api import Page
from src.data.LX.work_order.data_workorder_delect_edit_and_other import WorkorderData
from src.common.logger import logger


class WorkorderDelectEditAndOtherPage:
    def __init__(self, page: Page):
        self.page = page
        # 主页面导航定位器
        self.production_management = page.get_by_role("listitem", name="生产管理")
        self.production_workorder = page.get_by_text("生产工单")
        # 主页面iframe定位
        self.main_iframe_name = "WorkOrder"
        # 主页面iframe内按钮定位器
        self.add_button = "新 增"
        self.query_button = "查询"
        # 弹窗公共定位器
        self.order_no_input = "* 工单号"
        self.plan_qty_input = "* 计划产量"
        self.material_select_svg = 4
        self.material_row = "3 MAT_1775196603_WQRS 物料_WQRS"
        self.confirm_button = "确 定"
        self.auxiliary_select_locator = "div:nth-child(5) > div > .ant-row > .ant-col.ant-form-item-control > .ant-form-item-control-input > .ant-form-item-control-input-content > .ant-select > .ant-select-arrow > div > .anticon.anticon-search > svg"
        self.auxiliary_checkbox = ""
        self.save_button = "保 存"
        self.approve_button = "审 批"
    
    def navigate_to_workorder_page(self):
        """导航到生产工单页面"""
        logger.info("导航到生产工单页面...")
        self.production_management.click()
        self.production_workorder.click()
        self.page.wait_for_load_state('networkidle')
    
    def get_main_iframe(self):
        """获取生产工单主iframe"""
        logger.info("获取生产工单主iframe...")
        iframe = self.page.frame(self.main_iframe_name)
        if not iframe:
            raise Exception(f"无法找到名称为 {self.main_iframe_name} 的iframe")
        return iframe
    
    def click_add_button(self, iframe):
        """点击新增按钮并等待弹窗出现"""
        logger.info("点击新增按钮，打开新增工单弹窗...")
        with self.page.expect_popup() as modal_info:
            iframe.get_by_role("button", name=self.add_button).click()
        modal = modal_info.value
        modal.wait_for_load_state('networkidle')
        return modal
    
    def fill_workorder_modal(self, modal, order_no, plan_qty):
        """填写新增工单弹窗信息"""
        logger.info(f"填写新增工单信息：工单号={order_no}，计划产量={plan_qty}...")
        # 填写工单号
        order_no_elem = modal.get_by_role("textbox", name=self.order_no_input)
        order_no_elem.click()
        order_no_elem.fill(order_no)
        # 选择物料
        modal.locator("svg").nth(self.material_select_svg).click()
        modal.get_by_role("row", name=self.material_row).get_by_label(self.auxiliary_checkbox, exact=True).check()
        modal.get_by_role("button", name=self.confirm_button).click()
        # 填写计划产量
        plan_qty_elem = modal.get_by_role("spinbutton", name=self.plan_qty_input)
        plan_qty_elem.click()
        plan_qty_elem.fill(plan_qty)
        # 选择辅助项（暂未明确具体名称，按原逻辑操作）
        modal.locator(self.auxiliary_select_locator).click()
        modal.get_by_label(self.auxiliary_checkbox, exact=True).check()
        modal.get_by_role("button", name=self.confirm_button).click()
    
    def click_save_button(self, modal):
        """点击保存按钮"""
        logger.info("点击保存按钮...")
        modal.get_by_role("button", name=self.save_button).click()
    
    def click_approve_button(self, modal):
        """点击审批按钮"""
        logger.info("点击审批按钮...")
        modal.get_by_role("button", name=self.approve_button).click()
    
    def click_query_button(self, iframe):
        """点击查询按钮"""
        logger.info("点击查询按钮...")
        iframe.get_by_role("button", name=self.query_button).click()
        self.page.wait_for_load_state('networkidle')
    
    def check_workorder_row(self, iframe, order_no):
        """勾选指定工单号的行"""
        logger.info(f"勾选工单号为 {order_no} 的行...")
        row = iframe.get_by_role("row").filter(has_text=order_no)
        row.get_by_label(self.auxiliary_checkbox, exact=True).check()