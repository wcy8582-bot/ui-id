import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestFunOptimized(BaseTest):
    """
    用例名：fun_optimized
    用例ms的id：100946
    """

    def test_fun_optimized(self, page: Page, project_name: str):
        f"""测试产品档案新增启用质检控制功能
        用例名：fun_optimized
        用例ms的id：100946
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：fun_optimized")
        logger.info(f"用例ms的id：100946")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        logger.info("登录成功，开始菜单导航")
        
        # 点击基础资料菜单
        logger.info("点击基础资料菜单")
        page.locator("div").filter(has_text=re.compile(r"^基础资料$")).nth(2).click()
        
        # 进入产品档案页面
        logger.info("进入产品档案页面")
        page.get_by_text("产品档案").click()
        
        # 获取iframe内容上下文
        tab_iframe = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 点击新增产品按钮
        logger.info("点击新增产品按钮")
        tab_iframe.get_by_role("button", name="plus-circle 新增").click()
        
        # 勾选启用质检控制选项
        logger.info("操作勾选启用质检控制")
        tab_iframe.get_by_label("创建产品").get_by_text("启用质检控制").click()

        logger.info("操作勾选启用质检控制-是")
        tab_iframe.locator("#qualityControl .ant-radio-wrapper").first.click()
        
        logger.info("用例fun_optimized执行完成")