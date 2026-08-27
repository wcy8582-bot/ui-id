import os
import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestImportProductCodeExists(BaseTest):
    """
    用例名：import_product_code_exists
    用例ms的id：101240
    """

    def test_import_create_product(self, page: Page, project_name: str):
        f"""测试导入新增产品编码场景（客户资料列表导入）
        用例名：import_create_product
        用例ms的id：101240
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行测试用例：import_create_product")
        logger.info(f"用例ms的id：101240")
        logger.info("=" * 60)

        # 定义测试文件路径
        excel_file = r"D:\install\auto_ui-master\src\data\LD\customer_file\101240测试文件.xlsx"
        logger.info(f"测试文件: {excel_file}")

        if not os.path.exists(excel_file):
            raise FileNotFoundError(f"测试文件不存在: {excel_file}")

        # 使用封装好的公用登录方法登录系统
        logger.info("完成系统登录")
        self.login(page, project_name)

        # 进入客户档案模块
        logger.info("导航进入客户档案页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("客户档案").click()

        # 获取目标内容iframe
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame

        # 1. 定位客户资料页面
        logger.info("定位客户资料页面")
        customer_panel = frame.locator(".customer-list-left-panel")

        # 2. 点击客户资料页面的导入按钮
        logger.info("点击客户资料页面的导入按钮")
        customer_panel.locator("button", has_text="导入").click()
        
        # 3. 等待导入弹窗加载完成
        logger.info("等待导入弹窗出现")
        frame.get_by_role("dialog").wait_for(state="visible", timeout=5000)
        
        # 4. 上传文件并提交导入
        logger.info("上传导入文件，确认导入")
        frame.locator("input[type='file']").set_input_files(excel_file)
        frame.get_by_role("button", name="确 认").click()
        
        # 5. 等待导入完成并验证导入日志弹窗
        logger.info("等待导入完成")
        page.wait_for_timeout(3000)
        expect(frame.get_by_text("导入日志")).to_be_visible()

        # 6. 关闭弹窗，结束用例
        logger.info("关闭弹窗，用例执行完成")
        frame.get_by_role("button", name="关 闭").click()

        logger.info(f"测试用例import_create_product执行完成")