import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestLabelPrintConfigTest(BaseTest):
    """
    用例名：verify_left_and_right_list_interaction
    用例ms的id：101117
    """

    def test_verify_left_and_right_list_interaction(self, page: Page, project_name: str):
        f"""测试标签打印配置左右列表交互
        用例名：verify_left_and_right_list_interaction
        用例ms的id：101117
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_left_and_right_list_interaction")
        logger.info(f"用例ms的id：101117")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法
        self.login(page, project_name)

        # 导航进入标签打印配置页面
        logger.info("导航进入标签打印配置页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("系统配置").click()
        page.get_by_text("标签打印配置").click()

        # 获取标签内容iframe
        tab_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 选择托码分类，移除录制产生的重复点击操作
        logger.info("选择托码分类")
        tab_frame.locator("span").filter(has_text="托码").nth(1).click()
        
        # 点击新增按钮
        logger.info("点击新增按钮")
        tab_frame.get_by_role("button", name="plus-circle 新增").click()
        
        # 点击取消新增
        logger.info("点击取消新增按钮")
        tab_frame.get_by_role("button", name="取 消").click()

        logger.info("verify_left_and_right_list_interaction 用例执行完成")