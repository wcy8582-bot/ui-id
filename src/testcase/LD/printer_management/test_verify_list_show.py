import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestPrinterListShow(BaseTest):
    """
    用例名：verify_list_show
    用例ms的id：101138
    """

    def test_verify_list_show(self, page: Page, project_name: str):
        f"""测试打印机管理列表展示功能
        用例名：verify_list_show
        用例ms的id：101138
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例verify_list_show")
        logger.info(f"用例ms的id：101138")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 依次进入打印机管理菜单
        logger.info("进入打印机管理菜单")
        page.get_by_text("基础资料").click()
        page.get_by_text("系统配置").click()
        page.get_by_text("打印机管理").click()
        
        # 点击列表查询按钮
        logger.info("点击iframe内查询图标")
        page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("img").click()
        
        # 验证列表查询区域和表头正常显示
        logger.info("验证页面元素可见性")
        expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_text("序列号名称备注创建人请选择人员创建时间查 询重 置")).to_be_visible()
        expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_text("新增序号序列号名称备注创建人创建时间更新人更新时间操作")).to_be_visible()
        
        logger.info("用例verify_list_show执行完成")