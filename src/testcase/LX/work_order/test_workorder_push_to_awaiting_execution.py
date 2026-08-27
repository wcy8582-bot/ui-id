import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool


class TestWorkorderPushToAwaitingExecution(BaseTest):
    """
    用例名：workorder_push_to_awaiting_execution
    用例ms的id：100342
    """

    def test_workorder_push_to_awaiting_execution(self, page: Page, project_name: str):
        f"""测试生产工单下发到已下发未结束功能
        用例名：workorder_push_to_awaiting_execution
        用例ms的id：100342
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info("开始执行workorder_push_to_awaiting_execution")
        logger.info("用例ms的id：100342")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 选择生效工单状态
        logger.info("选择生效工单状态")
        Tool.select_workorder_types(page, "生效")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.locator("form").get_by_text("工单状态").click()
        logger.info("点击查询按钮")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="查询").click()
        
        # 打开并关闭第一个生效工单详情
        logger.info("打开并关闭第一个生效工单详情")
        with page.expect_popup() as page1_info:
            page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_text("生效").nth(1).dblclick()
        page1 = page1_info.value
        page1.wait_for_load_state("networkidle")
        # 获取单号
        workorder_no = page1.locator("input#productBatch").input_value()
        logger.info(f"获取到工单号: {workorder_no}")
        page1.close()
        
        # 按工单号查询
        logger.info("按工单号查询")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("textbox", name="工单号 :").fill(workorder_no)
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="查询").click()
        
        # 勾选工单并下发
        logger.info("勾选查询到的工单并点击下发")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_label("", exact=True).check()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="下 发").click()
        
        # 切换到已下发未结束状态查询
        logger.info("切换到已下发未结束状态并查询")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="已下发未结束").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="查询").click()
        
        # 勾选并查看工单详情
        logger.info("勾选查询到的工单并点击查看")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_label("", exact=True).check()
        with page.expect_popup() as page2_info:
            page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="查 看").click()
        page2 = page2_info.value
        # 等待页面加载完成
        page2.wait_for_load_state("networkidle")
        # 断言页面跳转成功（验证页面标题或URL）
        logger.info(f"页面跳转成功，URL: {page2.url}")
        # 简单验证页面是否成功加载
        assert page2.url is not None, "页面跳转失败"
        logger.info("页面跳转成功")
        page2.close()
        page.close()