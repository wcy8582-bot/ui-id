import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool

class TestWorkorderPushHideDiscard(BaseTest):
    """
    用例名：workorder_push_hide_discard
    用例ms的id：100196
    """

    def test_workorder_push_hide_discard(self, page: Page, project_name: str):
        f"""测试工单下发隐藏作废功能
        用例名：workorder_push_hide_discard
        用例ms的id：100196
        项目名：{project_name}
        用例描述：测试工单下发隐藏作废功能
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info("开始执行workorder_push_hide_discard")
        logger.info("用例ms的id：100196")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 在生产工单iframe内操作：选择状态、查询、勾选工单
        logger.info("在生产工单iframe内选择已下发未结束状态并查询")
        work_order_frame = page.locator("iframe[name=\"WorkOrder\"]").content_frame
        work_order_frame.get_by_role("button", name="已下发未结束").click()
        work_order_frame.get_by_role("button", name="查询").click()
        logger.info("勾选指定工单")
        work_order_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()

        # 断言隐藏废弃按钮
        logger.info("点击废弃按钮")
        view_button = work_order_frame.get_by_role("button", name="废 弃")
        Tool.assert_button_disabled(view_button, "废弃按钮")
        
        # 关闭页面
        logger.info("测试完成，关闭页面")
        page.close()