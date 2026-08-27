import re
import os
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestVerifyImportExists(BaseTest):
    """
    用例名：verify_import_exists
    用例ms的id：101315
    """

    def test_verify_import_exists(self, page: Page, project_name: str):
        f"""测试物料清单导入功能
        用例名：verify_import_exists
        用例ms的id：101315
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_import_exists")
        logger.info(f"用例ms的id：101315")
        logger.info("=" * 60)
        
        # 定义测试文件绝对路径
        excel_file = r"D:\install\auto_ui-master\src\data\LD\bom_management\物料清单_列表.xlsx"
        logger.info(f"测试文件: {excel_file}")
        
        if not os.path.exists(excel_file):
            raise FileNotFoundError(f"测试文件不存在: {excel_file}")
        
        # 使用封装好的公用登录方法登录系统
        logger.info("登录目标系统")
        self.login(page, project_name)
        
        # 导航进入物料清单页面
        logger.info("进入物料清单页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("物料清单").click()
        
        # 提取iframe内容框架，简化后续定位代码
        bom_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 打开导入弹窗
        logger.info("打开导入弹窗")
        expect(bom_frame.get_by_role("button", name="import 导入")).to_be_visible()
        bom_frame.get_by_role("button", name="import 导入").click()
        expect(bom_frame.get_by_text("文件选择模板下载")).to_be_visible()
        
        # 上传待导入的Excel文件
        logger.info("上传导入文件：工作簿5.xlsx")
        bom_frame.locator("input[type='file']").set_input_files(excel_file)
        expect(bom_frame.get_by_text("文件选择模板下载")).to_be_visible()
        
        # 确认导入并验证导入结果
        logger.info("确认导入，验证导入执行结果")
        bom_frame.get_by_role("button", name="确 认").click()
        page.wait_for_timeout(3000)
        expect(bom_frame.get_by_text("导入日志")).to_be_visible()
        
        # 关闭导入弹窗，用例结束
        logger.info("关闭导入弹窗")
        bom_frame.get_by_role("button", name="关 闭").click()
        
        logger.info(f"用例verify_import_exists执行完成")