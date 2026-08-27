import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyRequireField(BaseTest):
    """
    用例名：verify_require_field
    用例ms的id：101123
    """

    def test_verify_require_field(self, page: Page, project_name: str):
        f"""测试标签打印配置新增必填项校验
        用例名：verify_require_field
        用例ms的id：101123
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_require_field")
        logger.info(f"用例ms的id：101123")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法
        self.login(page, project_name)
        logger.info("登录成功，开始导航到目标页面")
        
        # 导航到标签打印配置页面
        logger.info("点击基础资料菜单")
        page.get_by_text("基础资料").click()
        logger.info("点击系统配置菜单")
        page.get_by_text("系统配置").click()
        logger.info("点击进入标签打印配置页面")
        page.get_by_text("标签打印配置").click()
        
        # 获取页面iframe上下文
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 空表单提交测试必填校验
        logger.info("点击新增按钮打开新增表单")
        frame.get_by_role("button", name="plus-circle 新增").click()
        logger.info("不填写任何内容，直接点击保存按钮")
        frame.get_by_role("button", name="保 存").click()
        logger.info("校验必填项提示信息是否正常显示")
        expect(frame.get_by_text("模板ID请输入模板ID模板名称请输入模板名称模板类型标签所属业务请选择所属业务")).to_be_visible()
        
        logger.info("点击取消关闭新增表单")
        frame.get_by_role("button", name="取 消").click()
        
        logger.info("用例verify_require_field执行完成")