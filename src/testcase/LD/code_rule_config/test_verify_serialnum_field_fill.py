import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifySerialnumFieldFill(BaseTest):
    """
    用例名：verify_serialnum_field_fill
    用例ms的id：101095
    """

    def test_verify_serialnum_field_fill(self, page: Page, project_name: str):
        f"""测试流水号字段配置功能
        用例名：verify_serialnum_field_fill
        用例ms的id：101095
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_serialnum_field_fill")
        logger.info(f"用例ms的id：101095")
        logger.info("=" * 60)

        # 使用公用登录方法
        self.login(page, project_name)

        # 进入编码规则配置页面
        logger.info("进入编码规则配置菜单")
        page.get_by_text("基础资料").click()
        page.get_by_text("编码规则配置").click()
        # 获取目标内容iframe
        logger.info("开始执行编码规则新增操作流程")
        target_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        target_frame.get_by_role("button", name="plus-circle 创建").click()
        
        target_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        target_frame.get_by_role("button", name="plus-circle 增行").click()
        
        target_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        target_frame.locator("#rc_select_4").wait_for(state="visible", timeout=10000)
        target_frame.locator("#rc_select_4").click()
        target_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        target_frame.get_by_text("流水号").click()
        
        # 点击"补位方式"列中显示"无"的下拉框
        target_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        target_frame.get_by_text("无").first.click()
        
        # 等待下拉选项展开后选择"左补位"
        page.wait_for_timeout(500)
        target_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        target_frame.get_by_text("左补位").first.click()
        # 再次点击"补位方式"下拉框（现在显示"左补位"），使用 nth(1) 定位表格中的下拉框
        page.wait_for_timeout(500)
        target_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        target_frame.get_by_text("左补位").nth(1).click()

        # 等待下拉选项展开后选择"左补位"
        page.wait_for_timeout(500)
        target_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        target_frame.get_by_text("右补位").first.click()
        
        logger.info("操作完成，点击取消退出")
        target_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        target_frame.get_by_role("button", name="取 消").click()