import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool



class TestWorkorderPushHideOther(BaseTest):
    """
    用例名：workorder_push_hide_other
    用例ms的id：100338
    """

    def test_workorder_push_hide_other(self, page: Page, project_name: str):
        f"""测试工单相关隐藏/其他推送功能
        用例名：workorder_push_hide_other
        用例ms的id：100338
        项目名：{project_name}
        用例描述：测试工单相关隐藏/其他推送功能
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info("开始执行workorder_push_hide_other")
        logger.info("用例ms的id：100338")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 测试编辑状态工单
        logger.info("测试编辑状态工单")
        Tool.select_workorder_types(page, "编辑")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("form").get_by_text("工单状态").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="查询").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        view_button = page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="下 发")
        # 验证按钮是否被禁用（置灰）
        Tool.assert_button_disabled(view_button, "下发按钮")

        # 测试审批状态工单
        logger.info("测试审批状态工单")
        Tool.select_workorder_types(page, "审批")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("form").get_by_text("工单状态").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="查询").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        view_button = page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="下 发")
        # 验证按钮是否被禁用（置灰）
        Tool.assert_button_disabled(view_button, "下发按钮")
        
        # 测试废弃状态工单
        logger.info("测试废弃状态工单")
        Tool.select_workorder_types(page, "废弃")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("form").get_by_text("工单状态").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="查询").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        view_button = page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="下 发")
        # 验证按钮是否被禁用（置灰）
        Tool.assert_button_disabled(view_button, "下发按钮")
        
        page.close()