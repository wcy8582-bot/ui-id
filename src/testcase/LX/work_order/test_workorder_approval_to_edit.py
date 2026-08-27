import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool



class TestWorkorderApprovalToEdit(BaseTest):
    """
    用例名：workorder_approval_to_edit
    用例ms的id：100729
    """

    def test_workorder_approval_to_edit(self, page: Page, project_name: str):
        f"""测试工单审批转编辑功能
        
        用例名：workorder_approval_to_edit
        用例ms的id：100729
        
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_approval_to_edit")
        logger.info(f"用例ms的id：100729")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 定位iframe并操作
        workorder_frame = page.locator("iframe[name=\"WorkOrder\"]").content_frame
        logger.info("操作工单状态下拉框")
        Tool.select_workorder_types(page, "编辑")
        workorder_frame.locator("form").get_by_text("工单状态").click()
        logger.info("点击查询按钮")
        workorder_frame.get_by_role("button", name="查询").click()
        
        # 打开编辑弹窗
        logger.info("打开编辑弹窗")
        with page.expect_popup() as page1_info:
            workorder_frame.get_by_text("编辑").nth(1).dblclick()
        page1 = page1_info.value
        page1.wait_for_load_state("networkidle")
        logger.info("复制工单号")
        page1.get_by_role("textbox", name="* 工单号").press("ControlOrMeta+a")
        page1.get_by_role("textbox", name="* 工单号").press("ControlOrMeta+c")
        logger.info("点击审批按钮")
        page1.get_by_role("button", name="审 批").click()
        page1.close()
           
        # 再次操作工单状态下拉框，选择审批状态
        logger.info("再次操作工单状态下拉框")
        Tool.select_workorder_types(page, "审批")
        workorder_frame.locator("form").get_by_text("工单状态").click()
        
        # 输入工单号查询
        logger.info("输入工单号并查询")
        workorder_frame.get_by_role("textbox", name="工单号 :").click()
        workorder_frame.get_by_role("textbox", name="工单号 :").press("ControlOrMeta+v")
        workorder_frame.get_by_role("button", name="查询").click()

        # 勾选并驳回
        logger.info("勾选工单并驳回")
        workorder_frame.get_by_label("", exact=True).check()
        workorder_frame.get_by_role("button", name="驳 回").click()
        
        # 再次操作工单状态下拉框，选择编辑状态
        logger.info("第三次操作工单状态下拉框")
        Tool.select_workorder_types(page, "编辑")
        workorder_frame.locator("form").get_by_text("工单状态").click()
                # 输入工单号查询
        logger.info("输入工单号并查询")
        workorder_frame.get_by_role("textbox", name="工单号 :").click()
        workorder_frame.get_by_role("textbox", name="工单号 :").press("ControlOrMeta+v")
        workorder_frame.get_by_role("button", name="查询").click()
        
        # 勾选并打开编辑弹窗
        logger.info("勾选工单并打开编辑弹窗")
        workorder_frame.get_by_label("", exact=True).check()
        with page.expect_popup() as page2_info:
            workorder_frame.get_by_role("button", name="编 辑").click()
        page2 = page2_info.value
        
        # 断言：验证页面是否成功跳转
        assert page2 is not None, "编辑页面未打开"
        assert not page2.is_closed(), "编辑页面已关闭"
        logger.info(f"编辑页面成功打开，URL: {page2.url}")
        
        page2.close()