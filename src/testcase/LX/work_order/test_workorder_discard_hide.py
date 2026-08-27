import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool



class TestWorkorderDiscardHide(BaseTest):
    """
    用例名：workorder_discard_hide
    用例ms的id：100386
    """

    def test_workorder_discard_hide(self, page: Page, project_name: str):
        f"""测试工单相关隐藏功能（基于核心操作）
        用例名：workorder_discard_hide
        用例ms的id：100386
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_discard_hide")
        logger.info(f"用例ms的id：100386")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()

        # 断言隐藏废弃按钮
        logger.info("点击废弃按钮")
        view_button = page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="废 弃")
        Tool.assert_button_disabled(view_button, "废弃按钮")
        
        # 关闭页面
        logger.info("测试完成，关闭页面")
        page.close()