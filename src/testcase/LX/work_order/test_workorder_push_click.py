import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool



class TestWorkOrderPush(BaseTest):
    """
    用例名：workorder_push_click
    用例ms的id：100339
    """

    def test_workorder_push_click(self, page: Page, project_name: str):
        f"""测试生产工单下发功能
        用例名：workorder_push_click
        用例ms的id：100339
        项目名：{project_name}
        用例描述：测试生产工单下发功能
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info("开始执行workorder_push_click")
        logger.info("用例ms的id：100339")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 操作工单状态筛选
        logger.info("操作工单状态筛选")
        Tool.select_workorder_types(page, "生效")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("form").get_by_text("工单状态").click()
        
        # 点击查询按钮
        logger.info("点击查询按钮")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="查询").click()
        
        # 勾选工单并点击下发
        logger.info("勾选工单并点击下发")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="下 发").click()
        
        # 验证操作成功完成提示
        logger.info("验证操作成功完成提示")
        page.wait_for_load_state("networkidle")
        success_message = page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("div").filter(has_text="操作成功完成").first
        expect(success_message).to_be_visible()
        
        page.close()