import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool



class TestWorkOrderApprovalStatus(BaseTest):
    """
    用例名：workorder_approval_status
    用例ms的id：100327
    """

    def test_workorder_approval_status(self, page: Page, project_name: str):
        f"""测试工单审批状态功能
        
        用例名：workorder_approval_status
        用例ms的id：100327
        
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_approval_status")
        logger.info(f"用例ms的id：100327")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 选择编辑并查询
        logger.info("选择编辑并查询")
        Tool.select_workorder_types(page, "编辑")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("form").get_by_text("工单状态").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="查询").click()
        
        # 选中工单并点击编辑
        logger.info("选中工单并点击编辑")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        with page.expect_popup() as page1_info:
            page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="编 辑").click()
        page1 = page1_info.value
        
        # 断言：验证页面是否成功跳转
        assert page1 is not None, "编辑页面未打开"
        assert not page1.is_closed(), "编辑页面已关闭"
        logger.info(f"编辑页面成功打开，URL: {page1.url}")
        
        page1.close()
        page.close()