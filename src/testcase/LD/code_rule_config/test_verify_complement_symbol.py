import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyComplementSymbol(BaseTest):
    """
    用例名：verify_complement_symbol
    用例ms的id：101074
    """

    def test_verify_complement_symbol(self, page: Page, project_name: str):
        f"""测试编码规则左补位符号配置功能
        用例名：verify_complement_symbol
        用例ms的id：101074
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_complement_symbol")
        logger.info(f"用例ms的id：101074")
        logger.info("=" * 60)

        # 使用公用登录方法
        self.login(page, project_name)

        # 进入编码规则配置页面
        logger.info("进入编码规则配置菜单")
        page.get_by_text("基础资料").click()
        page.get_by_text("编码规则配置").click()

        # 获取目标iframe内容帧
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 创建新编码规则，新增规则行
        logger.info("开始创建新编码规则")
        frame.get_by_role("button", name="plus-circle 创建").click()
        frame.get_by_role("button", name="plus-circle 增行").click()

        # 选择规则类型为流水号
        frame.locator("#rc_select_4").click()
        frame.get_by_text("流水号").click()

        # 配置流水号左补位，输入补位符号
        logger.info("配置流水号左补位参数")
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        frame.get_by_text("无").first.click()
        
        page.wait_for_timeout(500)
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        frame.get_by_text("左补位").first.click()
        
        page.wait_for_timeout(1000)
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        logger.info("开始输入1")
        frame.get_by_role("textbox").nth(5).click()
        frame.get_by_role("textbox").nth(5).type("1", delay=100)
        logger.info("输入1完成，开始清空")
        
        page.wait_for_timeout(500)
        frame.get_by_role("textbox").nth(5).evaluate("element => element.value = ''")
        logger.info("清空完成，开始输入q")
        
        page.wait_for_timeout(500)
        frame.get_by_role("textbox").nth(5).type("q", delay=100)
        logger.info("输入q完成")

        # 点击取消完成测试操作
        logger.info("完成操作，点击取消")
        frame.get_by_role("button", name="取 消").click()

        logger.info(f"用例verify_complement_symbol执行完毕")