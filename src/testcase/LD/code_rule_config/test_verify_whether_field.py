import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyWhetherField(BaseTest):
    """
    用例名：verify_whether_field
    用例ms的id：101106
    """

    def test_verify_whether_field(self, page: Page, project_name: str):
        f"""测试编码规则配置功能
        用例名：verify_whether_field
        用例ms的id：101106
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例verify_whether_field")
        logger.info(f"用例ms的id：101106")
        logger.info("=" * 60)

        # 使用公用登录方法
        self.login(page, project_name)

        # 进入编码规则配置页面
        logger.info("进入编码规则配置菜单")
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

        # 添加规则段并处理多余项
        logger.info("新增规则段并清理多余项")
        frame.get_by_role("button", name="plus-circle 增行").click()
        frame.locator("#rc_select_4").click()
        frame.get_by_text("日期时间").click()
        # 去除重复录制的多余点击，仅保留有效删除操作
        frame.get_by_role("button", name="holder 日期时间 日期时间 是 删除").click()
        frame.get_by_role("columnheader", name="* 是否显示 info-circle").click()
        frame.get_by_role("button", name="holder 日期时间 是 删除").click()
        
        # 取消新增操作
        logger.info("取消新增，结束用例")
        frame.get_by_role("button", name="取 消").click()