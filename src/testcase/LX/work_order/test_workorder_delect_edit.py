import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool



class TestWorkorderDelectEdit(BaseTest):
    """
    用例名：workorder_delect_edit
    用例ms的id：100192
    """

    def test_workorder_delect_edit(self, page: Page, project_name: str):
        f"""测试生产工单删除功能
        用例名：workorder_delect_edit
        用例ms的id：100192
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_delect_edit")
        logger.info(f"用例ms的id：100192")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 选择工单状态查询
        logger.info("选择工单状态并查询")
        workorder_frame = page.locator("iframe[name=\"WorkOrder\"]").content_frame
        Tool.select_workorder_types(page, "编辑")
        workorder_frame.locator("form").get_by_text("工单状态").click()
        workorder_frame.get_by_role("button", name="查询").click()
        
        # 执行删除工单操作
        logger.info("选中工单并执行删除")
        workorder_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        workorder_frame.get_by_role("button", name="删 除").click()
        workorder_frame.get_by_role("button", name="确 定").click()
        
        # 断言：验证操作成功完成
        logger.info("验证删除操作成功完成")
        success_message = workorder_frame.get_by_text("操作成功完成").first
        success_message.wait_for(timeout=10000)
        assert success_message.is_visible(), "删除操作成功完成提示未显示"
        logger.info("删除操作成功完成提示显示，测试通过")
        
        page.close()