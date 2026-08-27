import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestProductionOrderUpstreamNoSpace(BaseTest):
    """
    用例名：productionorder_upstream_no_space
    用例ms的id：100080
    """

    def test_productionorder_upstream_no_space(self, page: Page, project_name: str):
        f"""测试上游订单编号不能输入空格功能
        用例名：productionorder_upstream_no_space
        用例ms的id：100080
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行productionorder_upstream_no_space")
        logger.info(f"用例ms的id：100080")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产订单页面
        logger.info("进入生产订单页面")
        page.get_by_role("listitem", name="生产计划").click()
        page.get_by_text("生产订单").click()
        
        # 点击新增按钮
        logger.info("点击新增按钮")
        page.locator("iframe[name=\"ProductionOrders\"]").content_frame.get_by_role("button", name="新 增").click()
        
        # 获取iframe的content_frame作为变量简化后续操作
        content_frame = page.locator("iframe[name=\"ProductionOrders\"]").content_frame
        
        # 场景1：上游订单编号输入单个空格
        logger.info("验证上游订单编号输入单个空格的提示")
        content_frame.get_by_role("textbox", name="上游订单编号").fill(" ")
        expect(content_frame.locator("#sourceTableNo_help")).to_contain_text("不能输入空格")
        
        # 场景2：上游订单编号输入字母加空格
        logger.info("验证上游订单编号输入字母加空格的提示")
        content_frame.get_by_role("textbox", name="上游订单编号").fill("aaa ")
        expect(content_frame.locator("#sourceTableNo_help")).to_contain_text("不能输入空格")
        
        # 场景3：上游订单编号输入字母中间带空格
        logger.info("验证上游订单编号输入字母中间带空格的提示")
        content_frame.get_by_role("textbox", name="上游订单编号").fill("aaaa aaaaa")
        expect(content_frame.locator("#sourceTableNo_help")).to_contain_text("不能输入空格")
        
        logger.info("=" * 60)
        logger.info(f"执行完成productionorder_upstream_no_space")
        logger.info("=" * 60)