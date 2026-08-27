import re
from playwright.sync_api import Page
from src.data.LX.work_order.data_workorder_fuzzy_query import *
from src.common.logger import logger


class WorkorderFuzzyQueryPage:
    def __init__(self, page: Page):
        self.page = page
        # 主菜单元素定位器
        self.production_management = page.get_by_role("listitem", name="生产管理")
        self.work_order_menu = page.get_by_text("生产工单")
        
    def navigate_to_workorder_page(self):
        """导航到生产工单页面"""
        logger.info("进入生产工单页面")
        self.production_management.click()
        self.work_order_menu.click()
        self.page.wait_for_load_state('networkidle')
    
    def get_workorder_iframe(self):
        """获取生产工单iframe"""
        iframe = self.page.frame("WorkOrder")
        if not iframe:
            raise Exception("无法找到 WorkOrder iframe")
        return iframe
    
    def click_add_button(self, iframe):
        """点击新增按钮，获取新增弹窗页面对象"""
        logger.info("点击新增按钮，创建测试工单")
        with self.page.expect_popup() as page1_info:
            iframe.get_by_role("button", name="新 增").click()
        add_modal = page1_info.value
        return add_modal
    
    def fill_workorder_form(self, add_modal):
        """填写新增工单表单"""
        logger.info("填写新增工单表单")
        # 工单号
        add_modal.get_by_role("textbox", name="* 工单号").fill(WorkorderData["work_order_id"])
        # 清空默认选择的产品
        add_modal.get_by_role("button", name="close-circle").nth(1).click()
        # 生产批号
        add_modal.get_by_role("textbox", name="* 生产批号").fill(WorkorderData["batch_no"])
        # 选择产品
        add_modal.locator("svg").nth(4).click()
        add_modal.get_by_role("row").filter(has_text=WorkorderData["product_row_name"]).get_by_label("", exact=True).check()
        add_modal.get_by_role("button", name="确 定").click()
        # 计划产量
        add_modal.get_by_role("spinbutton", name="* 计划产量").fill(WorkorderData["planned_qty"])
        # 选择车间/产线
        add_modal.locator("div:nth-child(5) > div > .ant-row > .ant-col.ant-form-item-control > .ant-form-item-control-input > .ant-form-item-control-input-content > .ant-select > .ant-select-arrow > div > .anticon.anticon-search > svg").click()
        add_modal.get_by_label("", exact=True).check()
        add_modal.get_by_role("button", name="确 定").click()
        # 选择计划日期（仅点击触发框）
        add_modal.locator("div").filter(has_text=re.compile(r"^请输入$")).nth(4).click()
        # 选择状态（仅点击触发框）
        add_modal.locator("div:nth-child(13) > .ant-form-item > .ant-row > .ant-col.ant-form-item-control > .ant-form-item-control-input > .ant-form-item-control-input-content > .ant-select > .ant-select-selector").click()
        # 备注
        add_modal.get_by_role("textbox", name="备注").fill(WorkorderData["remark"])
    
    def save_workorder(self, add_modal):
        """保存工单并关闭弹窗"""
        logger.info("保存工单并关闭弹窗")
        add_modal.get_by_role("button", name="保 存").click()
        add_modal.close()
    
    def fuzzy_query_by_field(self, iframe, field_name, value):
        """根据字段名和模糊值查询"""
        logger.info(f"执行{field_name}模糊查询")
        field_locator = iframe.get_by_role("textbox", name=f"{field_name} :")
        field_locator.fill(value)
        iframe.get_by_role("button", name="查询").click()
    
    def clear_field(self, iframe, field_name):
        """清空指定查询字段"""
        logger.info(f"清空{field_name}查询字段")
        iframe.get_by_role("button", name="close-circle").first.click()
    
    def reset_query(self, iframe):
        """重置查询条件"""
        logger.info("重置查询条件")
        iframe.get_by_role("button", name="重置").click()
    
    def view_workorder(self, iframe):
        """查看工单（基础查看，不跳转指定URL）"""
        logger.info("查看工单详情")
        iframe.get_by_label("", exact=True).check()
        with self.page.expect_popup() as page2_info:
            iframe.get_by_role("button", name="查 看").click()
        view_modal = page2_info.value
        view_modal.close()
    
    def view_workorder_detail(self, iframe, detail_url):
        """查看工单详情（跳转指定URL后关闭）"""
        logger.info("查看工单详情（跳转指定URL）")
        iframe.get_by_role("row", name=f"1 {WorkorderData['work_order_id']}").get_by_label("", exact=True).check()
        with self.page.expect_popup() as page3_info:
            iframe.get_by_role("button", name="查 看").click()
        view_modal = page3_info.value
        view_modal.goto(detail_url)
        view_modal.get_by_role("button", name="关 闭").click()
        view_modal.close()