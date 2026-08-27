import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.data_generator import DataGenerator
from src.common.logger import logger

class TestLabelPrintTemplateAdd(BaseTest):
    """
    用例名：verify_template_name_field_check
    用例ms的id：101101
    """

    def test_verify_template_name_field_check(self, page: Page, project_name: str):
        f"""测试新增标签打印模板功能
        用例名：verify_template_name_field_check
        用例ms的id：101109
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_template_name_field_check")
        logger.info(f"用例ms的id：101109")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法
        self.login(page, project_name)
        
        # 导航至标签打印配置页面
        logger.info("导航到标签打印配置页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("系统配置").click()
        page.get_by_text("标签打印配置").click()

        # 获取iframe上下文，开始新增模板流程
        logger.info("进入新增模板流程，填写模板信息")
        sc_no = DataGenerator().get_pure_number_order_no()
        remark_text = DataGenerator().get_module_word()
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        frame.get_by_role("button", name="plus-circle 新增").click()
        frame.get_by_role("textbox", name="请输入模板ID").click()
        frame.get_by_role("textbox", name="请输入模板ID").fill(sc_no)
        frame.get_by_role("textbox", name="请输入模板名称").click()
        frame.get_by_role("textbox", name="请输入模板名称").fill(remark_text)
        frame.locator("div:nth-child(4) > .ant-row > .ant-col.ant-col-24 > .ant-form-item-control-input > .ant-form-item-control-input-content > .ant-select > .ant-select-selector > .ant-select-selection-item").click()
        frame.locator(".ant-select-dropdown .ant-select-item-option").nth(0).click()
        
        # 提交保存，验证结果
        logger.info("提交模板信息，验证保存结果")
        frame.get_by_role("button", name="保 存").click()
        frame.locator("div").filter(has_text="保存成功！").nth(3).click()
        
        logger.info("verify_template_name_field_check 用例执行完成")