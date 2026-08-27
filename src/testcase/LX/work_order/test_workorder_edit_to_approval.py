import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool



class TestWorkorderEditToApproval(BaseTest):
    """
    用例名：workorder_edit_to_approval
    用例ms的id：100199
    """

    def test_workorder_edit_to_approval(self, page: Page, project_name: str):
        """测试编辑工单后审批功能
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_edit_to_approval")
        logger.info(f"用例ms的id：100199")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 定位生产工单iframe
        wo_frame = page.locator("iframe[name='WorkOrder']").content_frame
        
        # 筛选工单状态并查询
        logger.info("筛选工单状态并查询")
        Tool.select_workorder_types(page, "编辑")
        wo_frame.locator("form").get_by_text("工单状态").click()
        wo_frame.get_by_role("button", name="查询").click()
        
        # 双击第二个编辑按钮弹出编辑页面并复制工单号
        logger.info("双击第二个编辑按钮并复制工单号")
        with page.expect_popup() as page1_info:
            wo_frame.get_by_text("编辑").nth(1).dblclick()
        page1 = page1_info.value
        page1.wait_for_load_state("networkidle")
        page1.get_by_role("textbox", name="* 工单号").press("ControlOrMeta+a")
        page1.get_by_role("textbox", name="* 工单号").press("ControlOrMeta+c")
        page1.close()
        
        # 粘贴工单号并查询
        logger.info("粘贴工单号并查询")
        wo_frame.get_by_role("textbox", name="工单号 :").press("ControlOrMeta+v")
        wo_frame.get_by_role("button", name="查询").click()
        
        # 勾选工单并审批
        logger.info("勾选工单并审批")
        wo_frame.get_by_label("", exact=True).check()
        wo_frame.get_by_role("button", name="审 批").click()
        
        # 再次输入工单号并查询
        logger.info("再次输入工单号并查询")
        Tool.select_workorder_types(page, "审批")
        wo_frame.get_by_role("textbox", name="工单号 :").press("ControlOrMeta+v")
        wo_frame.get_by_role("button", name="查询").click()
        
        # 验证工单状态为审批
        logger.info("验证工单状态为审批")
        expect(wo_frame.locator("tbody")).to_contain_text("审批")
