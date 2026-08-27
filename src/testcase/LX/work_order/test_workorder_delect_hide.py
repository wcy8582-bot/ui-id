import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool

class TestWorkorderDelectHide(BaseTest):
    """
    用例名：workorder_delect_hide
    用例ms的id：100322
    """

    def test_workorder_delect_hide(self, page: Page, project_name: str):
        f"""测试进入生产工单页面
        用例名：workorder_delect_hide
        用例ms的id：100322
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_delect_hide")
        logger.info(f"用例ms的id：100322")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("点击生产管理菜单")
        page.get_by_role("listitem", name="生产管理").click()
        logger.info("点击生产工单选项")
        page.get_by_text("生产工单").click()
        
        # 定位生产工单iframe
        logger.info("定位生产工单iframe")
        workorder_frame = page.locator("iframe[name=\"WorkOrder\"]").content_frame
        
        # 断言：验证删除按钮不可点击
        logger.info("验证删除按钮不可点击")
        delete_button = workorder_frame.get_by_role("button", name="删 除")
        
        # 检查按钮是否可见
        Tool.assert_button_disabled(delete_button, "删除按钮")
        
        page.close()