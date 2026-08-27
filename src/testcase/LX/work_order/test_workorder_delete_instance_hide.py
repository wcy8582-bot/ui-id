import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool


class TestWorkorderDeleteInstanceHide(BaseTest):
    """
    用例名：workorder_delete_instance_hide
    用例ms的id：100464
    """

    def test_workorder_delete_instance_hide(self, page: Page, project_name: str):
        f"""测试工单删除实例隐藏功能
        用例名：workorder_delete_instance_hide
        用例ms的id：100464
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_delete_instance_hide")
        logger.info(f"用例ms的id：100464")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        # 断言隐藏删除实例按钮
        logger.info("点击删除实例按钮")
        view_button = page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="删除实例")
        Tool.assert_button_disabled(view_button, "删除实例按钮")
        
        # 切换工单状态
        logger.info("切换工单状态：已下发未结束")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="已下发未结束").click()
        # 断言显示删除实例按钮
        logger.info("点击删除实例按钮")
        Tool.assert_button_disabled(view_button, "删除实例按钮")
        
        logger.info("切换工单状态：已结束")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="已结束").click()
        # 断言隐藏删除实例按钮
        logger.info("点击删除实例按钮")
        Tool.assert_button_disabled(view_button, "删除实例按钮")
        
        page.close()