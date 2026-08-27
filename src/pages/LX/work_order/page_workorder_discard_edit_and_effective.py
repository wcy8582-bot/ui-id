from playwright.sync_api import Page, Frame
from src.data.LX.work_order.data_workorder_discard_edit_and_effective import *
from src.common.logger import logger
from src.common.tool import Tool



class WorkorderDiscardEditAndEffectivePage:
    """生产工单新增、生效、勾选相关页面元素和操作封装"""
    def __init__(self, page: Page):
        self.page = page
        # 导航栏元素定位器（集中管理）
        self.nav_production_management = page.get_by_role("listitem", name=WorkorderData["nav_production_management"])
        self.nav_production_workorder = page.get_by_text(WorkorderData["nav_production_workorder"])
        # 主界面操作按钮定位器前缀（后续配合iframe使用）
        self.btn_add = "新 增"
        # 弹窗通用元素定位器
        self.btn_confirm = "确 定"
        self.btn_save = "保 存"
        self.btn_effective = "生 效"
        self.input_workorder_no = "* 工单号"
        self.input_plan_qty = "* 计划产量"
        self.svg_material_selector_prefix = "svg"
        self.div_second_selector_prefix = "div:nth-child({index}) > div > .ant-row > .ant-col.ant-form-item-control > .ant-form-item-control-input > .ant-form-item-control-input-content > .ant-select > .ant-select-arrow > div > .anticon.anticon-search > svg"
        self.material_row_locator = "get_by_role(\"row\", name=\"{row_name}\")"
        self.checkbox_exact = "get_by_label(\"\", exact=True)"
        self.workorder_row_locator = "get_by_role(\"row\", name=\"{row_no} {workorder_no}\")"
    
    def navigate_to_workorder_page(self):
        """导航到生产工单页面"""
        logger.info("导航到生产工单页面...")
        self.nav_production_management.click()
        self.nav_production_workorder.click()
        # 等待主界面iframe加载完成
        self.page.wait_for_load_state('networkidle')
        logger.info("生产工单页面加载完成")
    
    def get_main_iframe(self) -> Frame:
        """获取生产工单主iframe"""
        logger.info(f"获取名称为 {WorkorderData['main_iframe_name']} 的iframe...")
        iframe = self.page.frame(name=WorkorderData['main_iframe_name'])
        if not iframe:
            raise Exception(f"无法找到名称为 {WorkorderData['main_iframe_name']} 的主iframe")
        return iframe
    
    def click_add_button_and_get_popup(self, iframe: Frame):
        """在主iframe点击新增按钮并获取弹出页面"""
        logger.info("点击新增按钮打开工单新增弹窗...")
        with self.page.expect_popup() as popup_info:
            iframe.get_by_role("button", name=self.btn_add).click()
        popup = popup_info.value
        popup.wait_for_load_state('networkidle')
        logger.info("工单新增弹窗加载完成")
        return popup
    
    def fill_workorder_base_info(self, popup: Page, workorder_no: str, material_row_name: str, svg_material_index: int, div_second_select_index: int, plan_qty: str):
        """填写工单基础信息（工单号、物料、第二个选择项、计划产量）"""
        logger.info(f"填写工单基础信息，工单号：{workorder_no}")
        # 填写工单号
        popup.get_by_role("textbox", name=self.input_workorder_no).fill(workorder_no)
        # 点击物料选择器
        popup.locator(self.svg_material_selector_prefix).nth(svg_material_index).click()
        # 选择指定物料行
        material_row = popup.get_by_role("row").filter(has_text=material_row_name)
        material_row.get_by_label("", exact=True).check()
        popup.get_by_role("button", name=self.btn_confirm).click()
        # 点击第二个下拉选择器的搜索图标
        popup.locator(self.div_second_selector_prefix.format(index=div_second_select_index)).click()
        # 选择第二个下拉的第一条（默认勾选）
        popup.get_by_label("", exact=True).check()
        popup.get_by_role("button", name=self.btn_confirm).click()
        # 填写计划产量
        popup.get_by_role("spinbutton", name=self.input_plan_qty).fill(plan_qty)
        logger.info("工单基础信息填写完成")
    
    def create_and_save_workorder(self, iframe: Frame, workorder_no: str, material_row_name: str, svg_material_index: int, div_second_select_index: int, plan_qty: str):
        """创建工单并保存（完整流程）"""
        # 点击新增获取弹窗
        popup = self.click_add_button_and_get_popup(iframe)
        # 第一次点击保存（触发必填校验？原用例先填了部分保存）
        logger.info("第一次点击保存（部分必填后）")
        popup.get_by_role("button", name=self.btn_save).click()
        # 填写完整基础信息
        self.fill_workorder_base_info(popup, workorder_no, material_row_name, svg_material_index, div_second_select_index, plan_qty)
        # 第二次点击保存
        logger.info("第二次点击保存（完整信息后）")
        popup.get_by_role("button", name=self.btn_save).click()
        # 关闭弹窗
        popup.close()
    
    def create_and_effective_workorder(self, iframe: Frame, workorder_no: str, material_row_name: str, svg_material_index: int, div_second_select_index: int, plan_qty: str):
        """创建工单并生效（完整流程）"""
        # 点击新增获取弹窗
        popup = self.click_add_button_and_get_popup(iframe)
        # 填写完整基础信息
        self.fill_workorder_base_info(popup, workorder_no, material_row_name, svg_material_index, div_second_select_index, plan_qty)
        # 点击生效
        logger.info("点击生效按钮")
        popup.get_by_role("button", name=self.btn_effective).click()
        # 关闭弹窗
        popup.close()
    
    def check_two_workorders(self, iframe: Frame, row_no1: str, row_no2: str, workorder_no1: str, workorder_no2: str):
        """勾选指定的两个工单行（按行号和工单号组合定位）"""
        logger.info(f"勾选工单：{row_no1} {workorder_no1} 和 {row_no2} {workorder_no2}")
        # 勾选第一个工单（原用例的1 scgd20260414008）
        iframe.get_by_role("button", name="查询").click()
        iframe.get_by_role("row").filter(has_text=workorder_no1).get_by_label("", exact=True).check()
        # 勾选第二个工单（原用例的2 SCGD20260414007）
        iframe.get_by_role("row").filter(has_text=workorder_no2).get_by_label("", exact=True).check()

    def assert_discard_button_disabled(self, iframe: Frame):
        """断言废弃按钮是否置灰"""
        logger.info("断言废弃按钮置灰")
        view_button = iframe.get_by_role("button", name="废 弃")
        # 验证按钮是否被禁用（置灰）
        Tool.assert_button_disabled(view_button, "废弃按钮")
        