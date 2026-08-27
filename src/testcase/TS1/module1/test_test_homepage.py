import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestHomepage(BaseTest):
    """
    用例名：test_homepage
    用例ms的id：0
    """

    def test_homepage(self, page: Page, project_name: str):
        f"""测试首页登录功能
        用例名：test_homepage
        用例ms的id：0
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行test_homepage")
        logger.info(f"用例ms的id：0")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法
        logger.info("执行系统登录操作")
        self.login(page, project_name)
        
        # 点击确定完成登录后续操作
        logger.info("点击确定按钮完成登录流程")
        page.get_by_role("button", name="确定").click()
        
        logger.info("test_homepage用例执行完成")