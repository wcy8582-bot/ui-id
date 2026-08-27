import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestBatchCreateProduct(BaseTest):
    """
    用例名：batch_create
    用例ms的id：0
    """

    def test_batch_create(self, page: Page, project_name: str):
        f"""测试产品批量创建功能
        用例名：test_batch_create
        用例ms的id：0
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行test_batch_create")
        logger.info(f"用例ms的id：0")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入产品档案模块
        logger.info("进入基础资料-产品档案模块")
        page.get_by_text("基础资料").click()
        page.get_by_text("产品档案").click()
        
        # 获取产品档案iframe上下文，点击批量创建按钮
        logger.info("点击批量创建按钮")
        product_iframe = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        product_iframe.get_by_role("button", name="plus-circle 批量创建").click()
        
        # 断言批量编辑表格区域可见
        logger.info("断言批量创建表单区域可见")
        expect(product_iframe.locator("div").filter(has_text="增 行删 行序号产品编码产品名称产品规格产品型号产品类型单位产品属性标准工时产品来源工艺路线启用批次管理启用SN").nth(5)).to_be_visible()
        
        logger.info("batch_create执行完成")