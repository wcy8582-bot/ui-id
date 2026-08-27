import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifySerialnumField(BaseTest):
    """
    用例名：verify_serialnum_field
    用例ms的id：101096
    """

    def test_verify_serialnum_field(self, page: Page, project_name: str):
        f"""测试编码规则配置流水号字段
        用例名：verify_serialnum_field
        用例ms的id：101096
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_serialnum_field")
        logger.info(f"用例ms的id：101096")
        logger.info("=" * 60)

        # 使用公用登录方法
        self.login(page, project_name)
        logger.info("系统登录完成")

        # 进入编码规则配置页面
        logger.info("进入编码规则配置页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("编码规则配置").click()

        # 获取目标iframe上下文，去除重复定位代码
        iframe = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 执行创建增行操作，验证流水号选项
        logger.info("点击创建按钮")
        iframe.get_by_role("button", name="plus-circle 创建").click()
        logger.info("点击增行按钮")
        iframe.get_by_role("button", name="plus-circle 增行").click()
        logger.info("展开下拉选择类型")
        iframe.locator("#rc_select_4").click()
        logger.info("选择流水号选项")
        iframe.get_by_text("流水号").click()
        logger.info("点击取消完成操作")
        iframe.get_by_role("button", name="取 消").click()

        logger.info("verify_serialnum_field用例执行完成")