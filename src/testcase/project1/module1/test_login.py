import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestLogin(BaseTest):
    """
    用例名：login
    用例ms的id：0
    """

    def test_login(self, page: Page, project_name: str):
        f"""测试系统登录功能
        用例名：login
        用例ms的id：0
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行login")
        logger.info(f"用例ms的id：0")
        logger.info("=" * 60)
        
        # 打开登录页面
        logger.info("打开系统登录页面")
        page.goto("http://10.30.22.45:8080/login.html")
        
        # 输入用户名
        logger.info("输入登录用户名")
        page.get_by_role("textbox", name="请输入用户名").click()
        page.get_by_role("textbox", name="请输入用户名").fill("admin")
        
        # 输入登录密码，已去除录制生成的重复点击操作
        logger.info("输入登录密码")
        page.get_by_role("textbox", name="请输入密码").click()
        page.get_by_role("textbox", name="请输入密码").fill("Supcon@1304")
        
        # 点击登录按钮
        logger.info("点击登录按钮提交登录")
        page.get_by_role("button", name="登录").click()