import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.data_generator import DataGenerator
from src.common.logger import logger

class TestVerifyEditFunction(BaseTest):
    """
    用例名：verify_edit_function
    用例ms的id：101111
    """

    def test_verify_edit_function(self, page: Page, project_name: str):
        f"""测试标签打印配置编辑功能
        用例名：verify_edit_function
        用例ms的id：101123
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_edit_function")
        logger.info(f"用例ms的id：101123")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法
        logger.info("执行系统登录")
        self.login(page, project_name)
        
        # 导航到标签打印配置页面
        logger.info("导航进入标签打印配置页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("系统配置").click()
        page.get_by_text("标签打印配置").click()
        
        # 获取目标内容iframe，复用避免重复定位
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 打开目标条目的编辑弹窗
        logger.info("打开目标条目编辑")
        frame.get_by_text("编辑").nth(1).click()
        

        # 修改模板ID并保存
        logger.info("修改模板ID并保存")
        sc_no = DataGenerator().get_pure_number_order_no()
        frame.get_by_role("textbox", name="请输入模板ID").fill(sc_no)
        frame.get_by_role("button", name="保 存").click()
        
        logger.info("verify_edit_function用例执行完成")