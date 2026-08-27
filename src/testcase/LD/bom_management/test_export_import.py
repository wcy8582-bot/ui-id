import re
import os
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestBomImportExport(BaseTest):
    """
    用例名：export_import
    用例ms的id：101308
    """

    def test_export_import(self, page: Page, project_name: str):
        f"""测试物料清单导出后再导入功能
        用例名：export_import
        用例ms的id：101308
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：export_import")
        logger.info(f"用例ms的id：101308")
        logger.info("=" * 60)
        
        # 计算Excel文件路径 - 使用绝对路径
        excel_file_path = r"D:\install\auto_ui-master\src\data\LD\bom_management\101308测试导入.xlsx"
        logger.info(f"Excel文件路径: {excel_file_path}")

        # 调用公用登录方法
        logger.info("登录目标系统")
        self.login(page, project_name)

        # 导航到物料清单页面
        logger.info("进入基础资料->物料清单页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("物料清单").click()

        # 获取iframe上下文，避免重复定位
        bom_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 打开导入窗口，选择导入文件
        logger.info("打开导入窗口，上传测试文件")
        bom_frame.get_by_role("button", name="import 导入").click()
        
        # 等待文件选择器出现
        page.wait_for_timeout(2000)
        
        # 查找隐藏的 file input 元素
        file_input = bom_frame.locator("input[type='file']")
        file_input.set_input_files(excel_file_path)

        # 确认导入
        logger.info("校验弹窗提示，确认导入操作")
        expect(bom_frame.locator("div").filter(has_text="文件选择模板下载操作模式更新并新增导入说明:1.仅支持").nth(5)).to_be_visible()
        expect(bom_frame.get_by_role("button", name="确 认")).to_be_visible()
        bom_frame.get_by_role("button", name="确 认").click()

        # 校验导入结果
        logger.info("校验导入日志结果")
        # 等待导入操作完成
        page.wait_for_timeout(3000)
        expect(bom_frame.get_by_text("导入日志")).to_be_visible()
        # 检查是否有成功提示
        expect(bom_frame.get_by_text("成功").first).to_be_visible()

        # 关闭弹窗，结束用例
        logger.info("关闭导入弹窗，用例执行完成")
        expect(bom_frame.get_by_role("button", name="关 闭")).to_be_visible()
        bom_frame.get_by_role("button", name="关 闭").click()