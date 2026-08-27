import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool



class TestWorkorderDiscardEffectives(BaseTest):
    """
    用例名：workorder_discard_effectives
    用例ms的id：100388
    """

    def test_workorder_discard_effectives(self, page: Page, project_name: str):
        f"""测试工单废弃有效功能
        用例名：workorder_discard_effectives
        用例ms的id：100388
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_discard_effectives")
        logger.info(f"用例ms的id：100388")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 操作工单状态查询条件
        logger.info("操作工单状态查询条件")
        Tool.select_workorder_types(page, "生效")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("form").get_by_text("工单状态").click()
        
        # 执行查询操作
        logger.info("执行查询操作")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="查询").click()
        
        # 勾选目标工单
        logger.info("勾选目标工单")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("row").nth(2).get_by_label("", exact=True).check()
        
        # 执行废弃操作并确认
        logger.info("执行废弃操作并确认")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="废 弃").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="确 定").click()
        
        # 验证操作结果
        logger.info("验证操作结果")
        expect(page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("body")).to_contain_text("操作成功完成。")