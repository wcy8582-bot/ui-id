import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool



class TestWorkOrderDiscard(BaseTest):
    """
    用例名：workorder_discard
    用例ms的id：100194
    """

    def test_workorder_discard(self, page: Page, project_name: str):
        f"""测试生产工单废弃功能
        用例名：workorder_discard
        用例ms的id：100194
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_discard")
        logger.info(f"用例ms的id：100194")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 操作生产工单iframe内元素
        logger.info("开始操作生产工单废弃流程")
        Tool.select_workorder_types(page, "生效")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("form").get_by_text("工单状态").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="查询").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="废 弃").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="确 定").click()
        
        # 验证操作结果
        logger.info("验证操作结果")
        expect(page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("body")).to_contain_text("操作成功完成。")