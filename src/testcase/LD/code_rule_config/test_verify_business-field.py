import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyBusinessField(BaseTest):
    """
    用例名：verify_business-field
    用例ms的id：101093
    """

    def test_verify_business_field(self, page: Page, project_name: str):
        f"""测试编码规则配置中业务字段选择功能
        用例名：verify_business-field
        用例ms的id：101093
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行verify_business-field")
        logger.info(f"用例ms的id：101093")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法
        self.login(page, project_name)
        
        # 进入编码规则配置页面
        logger.info("导航到编码规则配置页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("编码规则配置").click()
        
        # 获取目标iframe上下文
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 执行新增流程操作
        logger.info("开始执行新增编码规则操作")
        frame.get_by_role("button", name="plus-circle 创建").click()
        frame.get_by_role("button", name="plus-circle 增行").click()
        frame.locator("#rc_select_4").click()
        frame.get_by_text("业务字段").click()
        
        # 取消新增，完成测试
        logger.info("点击取消，结束测试流程")
        frame.get_by_role("button", name="取 消").click()
        
        logger.info(f"用例verify_business-field执行完成")