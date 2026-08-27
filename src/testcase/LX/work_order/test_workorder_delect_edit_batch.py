import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool



class TestWorkorderDelectEditBatch(BaseTest):
    """
    用例名：workorder_delect_edit_batch
    用例ms的id：100324
    """

    def test_workorder_delect_edit_batch(self, page: Page, project_name: str):
        f"""测试批量删除生产工单功能
        用例名：workorder_delect_edit_batch
        用例ms的id：100324
        
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_delect_edit_batch")
        logger.info(f"用例ms的id：100324")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 选择工单状态为编辑
        logger.info("选择工单状态为编辑")
        Tool.select_workorder_types(page, "编辑")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("form").get_by_text("工单状态").click()
        
        # 点击查询按钮
        logger.info("点击查询按钮")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="查询").click()
        
        # 勾选两条待删除的生产工单
        logger.info("勾选两条待删除的生产工单")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("row").nth(2).get_by_label("", exact=True).check()
        
        # 点击删除按钮并确认
        logger.info("点击删除按钮并确认")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="删 除").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="确 定").click()
        
        # 断言：验证操作成功完成
        logger.info("验证批量删除操作成功完成")
        success_message = page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_text("操作成功完成").first
        success_message.wait_for(timeout=10000)
        assert success_message.is_visible(), "批量删除操作成功完成提示未显示"
        logger.info("批量删除操作成功完成提示显示，测试通过")
        
        logger.info("用例workorder_delect_edit_batch执行完成")