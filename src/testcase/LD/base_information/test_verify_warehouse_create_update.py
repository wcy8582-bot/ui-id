import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.data_generator import DataGenerator

class TestVerifyWarehouseCreateUpdate(BaseTest):
    """
    用例名：verify_warehouse_create_update
    用例ms的id：101011
    """

    def test_verify_warehouse_create_update(self, page: Page, project_name: str):
        f"""测试仓库创建功能
        用例名：verify_warehouse_create_update
        用例ms的id：101011
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_warehouse_create_update")
        logger.info(f"用例ms的id：101011")
        logger.info("=" * 60)
        
        # 调用封装好的公用登录方法
        logger.info("完成系统登录")
        self.login(page, project_name)
        
        # 导航到仓库管理页面
        logger.info("导航进入仓库管理页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("基础信息").click()
        page.get_by_text("仓库管理").first.click()
        
        # 提取iframe上下文，简化重复定位
        tab_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 打开创建仓库弹窗
        logger.info("点击创建按钮，打开创建仓库弹窗")
        tab_frame.get_by_role("button", name="plus-circle 创建").click()
        create_dialog = tab_frame.get_by_role("dialog", name="创建仓库")
        
        # 填写仓库基础信息
        logger.info("填写仓库编码和名称信息")
        ck_no = DataGenerator().get_order_no("ck")
        create_dialog.locator("#code").click()
        create_dialog.locator("#code").fill(ck_no)
        create_dialog.locator("#name").click()
        create_dialog.locator("#name").fill("创建按钮")
        
        # 选择仓库，去除录制产生的重复点击操作
        logger.info("选择仓库配置项")
        tab_frame.get_by_label("创建仓库").get_by_text("仓库", exact=True).click()
        
        # 保存新建的仓库
        logger.info("点击保存按钮完成创建")
        tab_frame.get_by_role("button", name="保 存").click()
        
        logger.info("verify_warehouse_create_update用例执行完成")