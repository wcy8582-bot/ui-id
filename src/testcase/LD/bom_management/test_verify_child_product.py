import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyChildProduct(BaseTest):
    """
    用例名：verify_child_product
    用例ms的id：100991
    """

    def test_verify_child_product(self, page: Page, project_name: str):
        f"""验证BOM子产品信息
        用例名：verify_child_product
        用例ms的id：100991
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行测试用例：verify_child_product")
        logger.info(f"用例ms ID：100991")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法登录系统
        self.login(page, project_name)

        # 导航到物料清单页面
        logger.info("导航到物料清单模块")
        page.get_by_text("基础资料").click()
        page.get_by_text("物料清单").click()
        
        # 获取BOM页面iframe上下文，简化后续调用
        bom_iframe = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 进入编辑状态，发起添加子项产品操作
        logger.info("进入编辑，发起添加子产品操作")
        bom_iframe.get_by_text("编辑").first.click()
        bom_iframe.get_by_role("button", name="plus-circle 添加子项产品").click()
        
        # 选择第一个产品并确认
        logger.info("选择目标子产品")
        bom_iframe.locator(".ant-table-cell > .ant-checkbox-wrapper").first.click()
        bom_iframe.get_by_role("button", name="选 择").click()
        
        # 执行关联工序相关操作
        logger.info("执行关联工序操作")
        bom_iframe.get_by_role("columnheader", name="关联工序").click()
        # 定位第三行关联工序下拉框（placeholder状态）并点击
        bom_iframe.locator("span.ant-select-selection-placeholder").nth(2).click()
        bom_iframe.get_by_role("columnheader", name="库存数量").click()

        # 点击取消完成测试
        logger.info("取消操作，结束测试")
        bom_iframe.get_by_role("button", name="取 消").click()
        
        logger.info(f"测试用例verify_child_product执行完成")