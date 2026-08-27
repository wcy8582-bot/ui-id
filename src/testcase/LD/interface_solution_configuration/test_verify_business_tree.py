import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyBusinessTree(BaseTest):
    """
    用例名：verify_business_tree
    用例ms的id：100879
    """

    def test_verify_business_tree(self, page: Page, project_name: str):
        f"""测试接口方案配置业务树展开功能
        用例名：verify_business_tree
        用例ms的id：100879
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_business_tree")
        logger.info(f"用例ms ID：100879")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法登录系统
        self.login(page, project_name)
        logger.info("登录成功，导航到目标功能页面")

        # 进入接口方案配置菜单
        page.get_by_text("基础资料").click()
        page.get_by_text("系统配置").click()
        page.get_by_text("接口方案配置").click()

        # 获取iframe上下文，优化重复获取iframe的冗余操作
        logger.info("逐层展开业务树折叠节点")
        tree_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        tree_frame.locator(".ant-tree-switcher.ant-tree-switcher_close").first.click()
        tree_frame.locator(".ant-tree-switcher.ant-tree-switcher_close").first.click()
        tree_frame.locator(".ant-tree-switcher.ant-tree-switcher_close").first.click()
        tree_frame.locator(".ant-tree-switcher.ant-tree-switcher_close").click()

        logger.info(f"用例verify_business_tree(ms ID: 100879)执行完成")