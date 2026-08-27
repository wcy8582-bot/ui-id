import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.data_generator import DataGenerator


class TestVerifyEditFunction(BaseTest):
    """
    用例名：verify_edit_function
    用例ms的id：101137
    """

    def test_verify_edit_function(self, page: Page, project_name: str):
        f"""测试打印机编辑功能
        用例名：verify_edit_function
        用例ms的id：101137
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_edit_function")
        logger.info(f"用例ms的id：101142")
        logger.info("=" * 60)
        
        # 使用公用登录方法登录系统
        logger.info("调用公用登录方法完成登录")
        self.login(page, project_name)
        
        # 导航到打印机管理页面
        logger.info("进入打印机管理菜单")
        page.get_by_text("基础资料").click()
        page.get_by_text("系统配置").click()
        page.get_by_text("打印机管理").click()
        
        # 获取目标iframe，执行编辑操作
        logger.info("执行编辑打印机信息操作")
        edit_iframe = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 等待列表加载
        logger.info("等待打印机列表加载")
        page.wait_for_timeout(1000)
        
        # 点击第一个编辑按钮
        logger.info("点击第一个'编辑'按钮")
        edit_iframe.get_by_text("编辑").first.click()
        
        # 填写备注信息
        logger.info("填写名称备注")
        remark_text = DataGenerator().get_module_word()
        edit_iframe.get_by_role("textbox", name="请输入名称备注").click()
        edit_iframe.get_by_role("textbox", name="请输入名称备注").fill(remark_text)
        edit_iframe.get_by_role("button", name="保 存").click()

        logger.info("用例verify_edit_function执行完成")