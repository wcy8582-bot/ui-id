import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestStandardTime(BaseTest):
    """
    用例名：standard_time
    用例ms的id：101193
    """

    def test_standard_time(self, page: Page, project_name: str):
        f"""测试新增产品标准工时功能
        用例名：standard_time
        用例ms的id：101193
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：standard_time")
        logger.info(f"用例ms的id：101193")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法登录系统
        self.login(page, project_name)
        logger.info("系统登录完成")

        # 进入产品档案模块
        logger.info("进入产品档案页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("产品档案").click()

        # 获取产品档案iframe上下文，简化后续定位
        product_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        # 点击新增产品按钮
        product_frame.get_by_role("button", name="plus-circle 新增").click()
        logger.info("点击新增产品按钮")

        # 点击标准工时选项，验证展示
        product_frame.get_by_label("创建产品").get_by_text("标准工时").click()
        logger.info("点击标准工时选项，开始验证展示效果")

        # 断言验证标准工时展示正常
        expect(product_frame.get_by_label("创建产品").locator("form")).to_contain_text("标准工时")
        expect(product_frame.locator("div").filter(has_text=re.compile(r"^标准工时小时分秒$")).first).to_be_visible()
        
        logger.info("所有断言通过，标准工时展示正常")
        logger.info(f"用例standard_time执行完成")