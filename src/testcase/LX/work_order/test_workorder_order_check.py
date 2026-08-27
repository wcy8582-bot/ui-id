import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool



class TestWorkOrderCheck(BaseTest):
    """
    用例名：workorder_order_check
    用例ms的id：100402
    """

    def test_workorder_order_check(self, page: Page, project_name: str):
        f"""测试生产工单各状态查看功能
        用例名：workorder_order_check
        用例ms的id：100402
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_order_check")
        logger.info(f"用例ms的id：100402")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 处理生产工单iframe
        workorder_frame = page.locator("iframe[name=\"WorkOrder\"]").content_frame
        
        # 查看编辑状态工单
        logger.info("查看编辑状态工单")
        Tool.select_workorder_types(page, "编辑")
        workorder_frame.locator("form").get_by_text("工单状态").click()
        workorder_frame.get_by_role("button", name="查询").click()
        workorder_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        with page.expect_popup() as page1_info:
            workorder_frame.get_by_role("button", name="查 看").click()
        page1 = page1_info.value
        page1.get_by_role("button", name="关 闭").click()
        page1.close()
        
        # 查看审批状态工单
        logger.info("查看审批状态工单")
        Tool.select_workorder_types(page, "审批")
        workorder_frame.locator("form").get_by_text("工单状态").click()
        workorder_frame.get_by_role("button", name="查询").click()
        workorder_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        with page.expect_popup() as page2_info:
            workorder_frame.get_by_role("button", name="查 看").click()
        page2 = page2_info.value
        page2.get_by_role("button", name="关 闭").click()
        page2.close()
        
        # 查看生效状态工单
        logger.info("查看生效状态工单")
        Tool.select_workorder_types(page, "生效")
        workorder_frame.locator("form").get_by_text("工单状态").click()
        workorder_frame.get_by_role("button", name="查询").click()
        workorder_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        with page.expect_popup() as page3_info:
            workorder_frame.get_by_role("button", name="查 看").click()
        page3 = page3_info.value
        page3.get_by_role("button", name="关 闭").click()
        page3.close()
        
        # 查看废弃状态工单
        logger.info("查看废弃状态工单")
        Tool.select_workorder_types(page, "废弃")
        workorder_frame.locator("form").get_by_text("工单状态").click()
        workorder_frame.get_by_role("button", name="查询").click()
        workorder_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        with page.expect_popup() as page4_info:
            workorder_frame.get_by_role("button", name="查 看").click()
        page4 = page4_info.value
        page4.get_by_role("button", name="关 闭").click()
        page4.close()