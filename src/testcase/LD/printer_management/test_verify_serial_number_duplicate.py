import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.data_generator import DataGenerator
from src.common.logger import logger


class TestVerifyCreateSave(BaseTest):
    """
    用例名：verify_serial_number_duplicate
    用例ms的id：101142
    """

    def test_verify_serial_number_duplicate(self, page: Page, project_name: str):
        f"""测试新增打印机功能——序列号重复校验
        用例名：verify_serial_number_duplicate
        用例ms的id：101142
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_serial_number_duplicate")
        logger.info(f"用例ms的id：101142")
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
        frame.get_by_role("textbox", name="请输入序列号").fill("666")

        # 填写名称备注
        remark_text = DataGenerator().get_module_word()
        frame.get_by_role("textbox", name="请输入名称备注").click()
        frame.get_by_role("textbox", name="请输入名称备注").fill(remark_text)

        # 保存新增打印机
        logger.info("点击保存按钮完成新增")
        frame.get_by_role("button", name="保 存").click()

        logger.info("用例verify_serial_number_duplicate执行完成")