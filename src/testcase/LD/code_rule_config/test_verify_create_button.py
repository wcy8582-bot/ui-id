import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyCreateButton(BaseTest):
    """
    用例名：verify_create_button
    用例ms的id：101097
    """

    def test_verify_create_button(self, page: Page, project_name: str):
        f"""测试新增编码规则功能
        用例名：verify_create_button
        用例ms的id：0
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行verify_create_button")
        logger.info(f"用例ms的id：0")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        logger.info("系统登录完成")
        
        # 进入编码规则配置页面
        logger.info("进入编码规则配置页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("编码规则配置").click()
        # 获取目标iframe
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame

        # 打开新增编码规则弹窗
        logger.info("打开新增编码规则弹窗，填写基础信息")
        frame.get_by_role("button", name="plus-circle 创建").click()

        frame.get_by_role("textbox", name="请输入规则名称").click()
        frame.get_by_role("textbox", name="请输入规则名称").fill("q")
        # 选择业务类型
        logger.info("定位业务类型下拉框")
        # 使用 .last 限定为弹窗内最新的下拉框，避开列表筛选栏的同名元素
        business_selector = frame.locator(".ant-select[name='业务类型']").last
        
        # 点击展开
        logger.info("点击业务类型下拉框")
        business_selector.click()
        
        # 等待下拉列表展开
        logger.info("等待下拉列表展开")
        frame.locator(".ant-select-dropdown").wait_for(state="visible", timeout=5000)
        
        # 使用 nth 索引动态获取下拉选项
        logger.info("动态选择业务类型（索引 0）")
        frame.locator(".ant-select-item-option").nth(0).click()


        # 新增规则段配置
        logger.info("添加日期格式规则段")
        frame.get_by_role("button", name="plus-circle 增行").click()
        frame.locator("#rc_select_4").click()
        frame.get_by_text("日期时间").click()
        frame.locator("#rc_select_6").click()
        frame.get_by_text("yy").nth(2).click()

        # 保存规则并执行停用
        logger.info("保存编码规则并执行停用操作")
        frame.get_by_role("button", name="保 存").click()
        frame.get_by_role("cell", name="AA00006").click()
        frame.get_by_role("cell", name="停用").first.click()

        logger.info("verify_create_button用例执行完成")