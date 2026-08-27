import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool



class TestWorkOrderEditButtonCantClick(BaseTest):
    """
    用例名：workorder_edit_button_cant_click
    用例ms的id：100330
    """

    def test_workorder_edit_button_cant_click(self, page: Page, project_name: str):
        f"""测试生产工单编辑按钮不可点击功能
        用例名：workorder_edit_button_cant_click
        用例ms的id：100330
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_edit_button_cant_click")
        logger.info(f"用例ms的id：100330")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 操作生产工单iframe内的内容
        logger.info("操作生产工单iframe内的内容")
        workorder_frame = page.locator("iframe[name=\"WorkOrder\"]").content_frame
        Tool.select_workorder_types(page, "审批")
        workorder_frame.locator("form").get_by_text("工单状态").click()
        workorder_frame.get_by_role("button", name="查询").click()
        
        # 选择列表内的第一条数据
        logger.info("选择列表内的第一条数据")
        first_row = workorder_frame.get_by_role("row").nth(1)
        first_row.get_by_label("", exact=True).check()
        
        # 测试编辑按钮是否被置灰
        edit_button = workorder_frame.get_by_role("button", name="编 辑")
        Tool.assert_button_disabled(edit_button, "编辑按钮")
        
        Tool.select_workorder_types(page, "生效")
        workorder_frame.locator("form").get_by_text("工单状态").click()
        workorder_frame.get_by_role("button", name="查询").click()
        
        # 选择列表内的第一条数据
        logger.info("选择列表内的第一条数据")
        first_row = workorder_frame.get_by_role("row").nth(1)
        first_row.get_by_label("", exact=True).check()
        
        # 测试编辑按钮是否被置灰
        edit_button = workorder_frame.get_by_role("button", name="编 辑")
        Tool.assert_button_disabled(edit_button, "编辑按钮")
        
        page.close()