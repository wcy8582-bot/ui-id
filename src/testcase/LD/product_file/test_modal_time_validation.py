import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.data_generator import DataGenerator
from src.common.logger import logger

class TestModalTimeValidation(BaseTest):
    """
    用例名：modal_time_validation
    用例ms的id：101190
    """

    def test_modal_time_validation(self, page: Page, project_name: str):
        f"""测试产品档案标准工时验证功能
        用例名：modal_time_validation
        用例ms的id：101190
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：modal_time_validation")
        logger.info(f"用例ms的id：101190")
        logger.info("=" * 60)
        
        # 使用公用登录方法登录系统
        logger.info("调用公用登录方法完成登录")
        self.login(page, project_name)
        
        # 导航到产品档案页面
        logger.info("进入基础资料->产品档案页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("产品档案").click()

        # 获取产品档案iframe上下文，简化后续调用
        product_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 点击新增产品按钮
        logger.info("点击新增产品按钮")
        product_frame.get_by_role("button", name="plus-circle 新增").click()

        # 验证新增产品弹窗基础元素可见
        logger.info("验证新增弹窗核心元素可见性")
        expect(product_frame.get_by_label("创建产品")).to_be_visible()
        expect(product_frame.get_by_label("创建产品").get_by_text("标准工时")).to_be_visible()
        expect(product_frame.locator("div").filter(has_text=re.compile(r"^标准工时小时分秒$")).first).to_be_visible()

        # 输入标准工时初始值
        logger.info("测试标准工时手动输入")
        hour_value = DataGenerator().get_random_hour()
        product_frame.get_by_role("spinbutton").first.click()
        product_frame.get_by_role("spinbutton").first.fill(str(hour_value))
        expect(product_frame.locator("div").filter(has_text=re.compile(r"^标准工时小时分秒$")).first).to_be_visible()

        # 测试增加值按钮
        logger.info("测试标准工时增加按钮功能")
        product_frame.get_by_role("button", name="Increase Value").first.click()
        product_frame.get_by_role("button", name="Increase Value").first.click()
        expect(product_frame.locator("div").filter(has_text=re.compile(r"^标准工时小时分秒$")).first).to_be_visible()

        # 测试减少值按钮
        logger.info("测试标准工时减少按钮功能")
        expect(product_frame.get_by_role("button", name="Decrease Value").first).to_be_visible()
        product_frame.get_by_role("button", name="Decrease Value").first.click()
        product_frame.get_by_role("button", name="Decrease Value").first.click()
        expect(product_frame.locator("div").filter(has_text=re.compile(r"^标准工时小时分秒$")).first).to_be_visible()

        logger.info("用例modal_time_validation执行完成")