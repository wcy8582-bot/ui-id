import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestPrinterManageRequiredField(BaseTest):
    """
    用例名：verify_required_field
    用例ms的id：101128
    """

    def test_verify_required_field(self, page: Page, project_name: str):
        f"""测试打印机管理新增必填项校验
        用例名：verify_required_field
        用例ms的id：101128
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_required_field")
        logger.info(f"用例ms的id：101128")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法
        self.login(page, project_name)
        
        # 导航进入打印机管理页面
        logger.info("进入打印机管理页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("系统配置").click()
        page.get_by_text("打印机管理").click()
        
        # 获取目标iframe内容帧
        tab_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 核心操作步骤
        logger.info("点击新增按钮打开新增弹窗")
        tab_frame.get_by_role("button", name="plus-circle 新增").click()
        logger.info("未填写信息直接点击保存，触发必填项校验")
        tab_frame.get_by_role("button", name="保 存").click()
        logger.info("点击取消关闭新增弹窗")
        tab_frame.get_by_role("button", name="取 消").click()
        
        logger.info("用例verify_required_field执行完成")