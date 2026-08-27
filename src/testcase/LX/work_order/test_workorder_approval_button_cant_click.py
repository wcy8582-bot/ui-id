import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool

class TestWorkOrderApprovalButtonCantClick(BaseTest):
    """
    用例名：workorder_approval_button_cant_click
    用例ms的id：100329
    """

    def test_workorder_approval_button_cant_click(self, page: Page, project_name: str):
        f"""测试生产工单审批按钮不可点击功能

        用例名：workorder_approval_button_cant_click
        用例ms的id：100329

        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_approval_button_cant_click")
        logger.info(f"用例ms的id：100329")
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
        Tool.select_workorder_types(page, "生效")
        workorder_frame.locator("form").get_by_text("工单状态").click()
        workorder_frame.get_by_role("button", name="查询").click()
        
        # 选择列表内的第一条数据
        logger.info("选择列表内的第一条数据")
        first_row = workorder_frame.get_by_role("row").nth(1)
        first_row.get_by_label("", exact=True).check()
        
        # 测试审批按钮是否被置灰
        logger.info("测试审批按钮是否被置灰（编辑状态工单）")
        approval_button = workorder_frame.get_by_role("button", name="审 批")
        Tool.assert_button_disabled(approval_button, "审批按钮")

        page.close()
