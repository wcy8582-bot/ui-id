import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestVerifyConstantField(BaseTest):
    """
    用例名：verify_constant_field
    用例ms的id：101099
    """

    def test_verify_constant_field(self, page: Page, project_name: str):
        f"""测试编码规则固定值字段配置功能
        用例名：verify_constant_field
        用例ms的id：101099
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_constant_field")
        logger.info(f"用例ms ID：101099")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法
        logger.info("执行系统登录")
        self.login(page, project_name)
        
        # 导航到编码规则配置页面
        logger.info("进入编码规则配置页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("编码规则配置").click()

        # 获取iframe上下文，开始测试固定值配置
        logger.info("开始新增编码规则，测试固定字段输入")
        content_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        content_frame.get_by_role("button", name="plus-circle 创建").click()
        content_frame.get_by_role("button", name="plus-circle 增行").click()
        content_frame.locator("#rc_select_4").click()
        content_frame.get_by_title("固定值").click()
        content_frame.get_by_role("textbox").nth(5).click()
        content_frame.get_by_role("textbox").nth(5).fill("ly")
        
        logger.info("测试操作完成，点击取消")
        content_frame.get_by_role("button", name="取 消").click()