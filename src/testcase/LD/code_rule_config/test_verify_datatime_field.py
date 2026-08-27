import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyDataField(BaseTest):
    """
    用例名：verify_datatime_field
    用例ms的id：101101
    """

    def test_verify_datatime_field(self, page: Page, project_name: str):
        f"""验证日期时间字段类型
        用例名：verify_data_field
        用例ms的id：101101
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_datatime_field")
        logger.info(f"用例ms的id：101101")
        logger.info("=" * 60)

        # 使用公用登录方法
        self.login(page, project_name)

        # 进入编码规则配置页面
        logger.info("进入编码规则配置菜单")
        page.get_by_text("基础资料").click()
        page.get_by_text("编码规则配置").click()
        
        # 提取目标iframe，避免重复定位
        tab_iframe = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        logger.info("开始执行编码规则新增操作")
        
        # 点击创建按钮
        tab_iframe.get_by_role("button", name="plus-circle 创建").click()
        # 点击增行按钮
        tab_iframe.get_by_role("button", name="plus-circle 增行").click()
        # 选择分段类型
        tab_iframe.locator("#rc_select_4").click()
        tab_iframe.get_by_text("日期时间").click()
        # 选择日期格式
        tab_iframe.locator("#rc_select_6").click()
        tab_iframe.get_by_text("yy").nth(2).click()
        # 点击取消完成操作
        tab_iframe.get_by_role("button", name="取 消").click()
        
        logger.info(f"用例verify_datatime_field执行完成")