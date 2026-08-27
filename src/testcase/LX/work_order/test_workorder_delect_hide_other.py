import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool



class TestWorkorderDelectHideOther(BaseTest):
    """
    用例名：workorder_delect_hide_other
    用例ms的id：100195
    """

    def test_workorder_delect_hide_other(self, page: Page, project_name: str):
        f"""测试工单删除隐藏其他功能
        用例名：workorder_delect_hide_other
        用例ms的id：100195
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_delect_hide_other")
        logger.info(f"用例ms的id：100195")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 第一次查询及操作
        logger.info("执行第一次查询及选择操作")
        Tool.select_workorder_types(page, "审批")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("form").get_by_text("工单状态").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="查询").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        # 定位按钮
        view_button = page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="删 除")
        # 验证按钮是否被禁用（置灰）
        Tool.assert_button_disabled(view_button, "删除按钮")
        
        # 第二次查询及操作
        logger.info("执行第二次查询及选择操作")
        Tool.select_workorder_types(page, "生效")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("form").get_by_text("工单状态").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="查询").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
                # 定位按钮
        view_button = page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="删 除")
        # 验证按钮是否被禁用（置灰）
        Tool.assert_button_disabled(view_button, "删除按钮")
        
        # 第三次查询及操作
        logger.info("执行第三次查询及选择操作")
        Tool.select_workorder_types(page, "废弃")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("form").get_by_text("工单状态").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="查询").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
                # 定位按钮
        view_button = page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="删 除")
        # 验证按钮是否被禁用（置灰）
        Tool.assert_button_disabled(view_button, "删除按钮")
        
        page.close()