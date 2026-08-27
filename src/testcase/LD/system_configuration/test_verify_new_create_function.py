import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.data_generator import DataGenerator
from src.common.logger import logger


class TestLabelPrintTemplateCreate(BaseTest):
    """
    用例名：verify_new_create_function
    用例ms的id：101113
    """

    def test_verify_new_create_function(self, page: Page, project_name: str):
        f"""测试新增标签打印配置功能
        用例名：verify_new_create_function
        用例ms的id：101113
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_new_create_function")
        logger.info(f"用例ms的id：101113")
        logger.info("=" * 60)

        # 使用公用登录方法
        self.login(page, project_name)
        logger.info("系统登录完成，开始业务操作")

        # 导航进入标签打印配置页面
        logger.info("导航进入标签打印配置页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("系统配置").click()
        page.get_by_text("标签打印配置").click()

        # 获取业务内容iframe，简化重复定位代码
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        logger.info("获取业务iframe完成，开始新增操作")

        # 点击新增按钮
        frame.get_by_role("button", name="plus-circle 新增").click()

        # 填写模板信息，去除录制生成的多余点击操作，fill可自动激活输入框
        logger.info("填写模板基础信息")
        sc_no = DataGenerator().get_pure_number_order_no()
        remark_text = DataGenerator().get_module_word()
        frame.get_by_role("textbox", name="请输入模板ID").fill(sc_no)
        frame.get_by_role("textbox", name="请输入模板名称").fill(remark_text)

        # 选择模板类型
        logger.info("选择模板类型")
        frame.locator(
            "div:nth-child(4) > .ant-row > .ant-col.ant-col-24 > .ant-form-item-control-input > .ant-form-item-control-input-content > .ant-select > .ant-select-selector > .ant-select-selection-item").click()
        frame.locator(".ant-select-dropdown .ant-select-item-option").nth(0).click()

        # 保存新增模板
        logger.info("点击保存按钮完成新增")
        frame.get_by_role("button", name="保 存").click()

        logger.info(f"用例verify_new_create_function执行完成")