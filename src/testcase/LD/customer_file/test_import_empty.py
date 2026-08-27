import os
import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestImportEmpty(BaseTest):
    """
    用例名：import_empty
    用例ms的id：101271
    """

    def test_import_empty(self, page: Page, project_name: str):
        f"""测试导入空表
        用例名：import_empty
        用例ms的id：101271
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：import_empty")
        logger.info(f"用例ms ID：101271")
        logger.info("=" * 60)
        # 定义测试文件路径
        excel_file = r"D:\install\auto_ui-master\src\data\LD\customer_file\空表.xlsx"
        logger.info(f"测试文件: {excel_file}")

        if not os.path.exists(excel_file):
            raise FileNotFoundError(f"测试文件不存在: {excel_file}")
        
        # 使用封装好的公用登录方法登录系统
        logger.info("调用公用登录方法登录系统")
        self.login(page, project_name)
        
        # 处理登录后弹窗，进入客户档案模块
        logger.info("进入客户档案页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("客户档案").click()
        
        # 提取iframe
        tab_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 1. 定位客户资料页面
        logger.info("定位客户资料页面")
        customer_panel = tab_frame.locator(".customer-list-left-panel")
        
        # 2. 精确定位第一个数据行（排除表头和隐藏行）
        logger.info("定位第一个客户数据行")
        first_customer_row = customer_panel.locator("tbody.ant-table-tbody tr.ant-table-row").first
        
        # 3. 点击该行激活右侧页面
        logger.info("点击第一个客户数据行，激活客户产品映射页面")
        first_customer_row.click()
        
        # 4. 等待客户行被选中
        logger.info("等待客户行选中状态")
        customer_panel.locator("tbody tr.customer-list-selected-row").first.wait_for(state="visible", timeout=5000)
        
        # 5. 定位右侧客户产品映射面板的导入按钮
        logger.info("定位客户产品映射区域的导入按钮")
        mapping_panel = tab_frame.locator(".customer-list-right-panel")
        import_btn = mapping_panel.locator("button", has_text="导入")
        
        # 6. 等待导入按钮可用
        logger.info("等待导入按钮可用")
        import_btn.wait_for(state="visible", timeout=5000)
        
        # 7. 点击导入按钮
        logger.info("点击导入按钮")
        import_btn.click()
        
        # 8. 上传文件并提交导入
        logger.info("上传导入文件，确认导入")
        tab_frame.locator("input[type='file']").set_input_files(excel_file)
        tab_frame.get_by_role("button", name="确 认").click()
        
        # 9. 等待导入完成并验证导入日志弹窗
        logger.info("等待导入完成")
        page.wait_for_timeout(3000)
        expect(tab_frame.get_by_text("导入日志")).to_be_visible()

        # 10. 关闭弹窗，结束用例
        logger.info("关闭弹窗，用例执行完成")
        tab_frame.get_by_role("button", name="关 闭").click()