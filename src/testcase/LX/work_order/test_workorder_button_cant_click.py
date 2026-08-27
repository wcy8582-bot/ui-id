import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool

class TestWorkOrderCantClick(BaseTest):
    """
    用例名：workorder_button_cant_click
    用例ms的id：100326
    """

    def test_workorder_button_cant_click(self, page: Page, project_name: str):
        f"""测试生产工单新增按钮相关功能
        用例名：workorder_button_cant_click
        用例ms的id：100326
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_button_cant_click")
        logger.info(f"用例ms的id：100326")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 测试置灰按钮能否点击
        logger.info("测试置灰按钮能否点击")
        iframe = page.locator("iframe[name=\"WorkOrder\"]").content_frame
        buttons = ["编 辑", "审 批", "生 效", "驳 回", "废 弃", "查 看", "下 发", "停 止", "删 除", "删除实例"]
        
        for button_name in buttons:
            button = iframe.get_by_role("button", name=button_name)
            logger.info(f"检查按钮状态: {button_name}")
            
            # 检查按钮是否被禁用
            Tool.assert_button_disabled(button, button_name)
        
        page.close()