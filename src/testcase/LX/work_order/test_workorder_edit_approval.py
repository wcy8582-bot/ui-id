import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool



class TestWorkorderEditApproval(BaseTest):
    """
    用例名：workorder_edit_approval
    用例ms的id：100200
    """

    def test_workorder_edit_approval(self, page: Page, project_name: str):
        f"""测试工单编辑审批功能
        用例名：workorder_edit_approval
        用例ms的id：100200
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_edit_approval")
        logger.info(f"用例ms的id：100200")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 切换到生产工单iframe
        logger.info("切换到生产工单iframe")
        workorder_frame = page.locator("iframe[name=\"WorkOrder\"]").content_frame
        
        # 第一次操作：选择状态并审批
        logger.info("第一次操作：选择状态并审批")
        Tool.select_workorder_types(page, "编辑")
        workorder_frame.locator("form").get_by_text("工单状态").click()
        workorder_frame.get_by_role("button", name="查询").click()
        workorder_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        workorder_frame.get_by_role("button", name="审 批").click()
                
        # 验证操作结果
        logger.info("验证操作结果")
        expect(page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("body")).to_contain_text("操作成功完成。")