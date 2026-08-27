import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.data_generator import DataGenerator

class TestVerifyCreateSave(BaseTest):
    """
    用例名：verify_create_save
    用例ms的id：101143
    """

    def test_verify_create_save(self, page: Page, project_name: str):
        f"""测试新增打印机功能
        用例名：verify_create_save
        用例ms的id：101143
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_create_save")
        logger.info(f"用例ms的id：101143")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        logger.info("完成系统登录")
        self.login(page, project_name)
        
        # 导航进入打印机管理页面
        logger.info("导航进入打印机管理菜单")
        page.get_by_text("基础资料").click()
        page.get_by_text("系统配置").click()
        page.get_by_text("打印机管理").click()
        
        # 获取内容iframe，简化重复定位
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 点击新增按钮开始创建
        logger.info("点击新增按钮，填写打印机信息")
        frame.get_by_role("button", name="plus-circle 新增").click()
        
        # 填写序列号
        frame.get_by_role("textbox", name="请输入序列号").click()
        dy_no = DataGenerator().get_order_no()
        frame.get_by_role("textbox", name="请输入序列号").fill(dy_no)
        
        # 填写名称备注
        frame.get_by_role("textbox", name="请输入名称备注").click()
        frame.get_by_role("textbox", name="请输入名称备注").fill("测试")
        
        # 保存新增打印机
        logger.info("点击保存按钮完成新增")
        frame.get_by_role("button", name="保 存").click()


        logger.info("用例verify_create_save执行完成")