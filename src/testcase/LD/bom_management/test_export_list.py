import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestExportList(BaseTest):
    """
    用例名：export_list
    用例ms的id：101309
    """

    def test_export_list(self, page: Page, project_name: str):
        f"""测试物料清单导出功能
        用例名：export_list
        用例ms的id：101309
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：export_list")
        logger.info(f"用例ms的id：101309")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法登录系统
        self.login(page, project_name)
        
        # 进入物料清单菜单
        logger.info("进入物料清单页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("物料清单").click()

        # 验证导出元素存在
        expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("#root")).to_contain_text("导出")
        export_btn = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="export 导出")
        expect(export_btn).to_be_visible()
        
        # 打开导出弹窗
        logger.info("点击导出按钮打开导出配置弹窗")
        export_btn.click()

        # 验证导出弹窗信息正确
        expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_label("导出").get_by_text("导出", exact=True)).to_be_visible()
        expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_text("文件名：导出数据范围：选中页面范围全部数据 — （请输入页码范围（例如：1-3））")).to_be_visible()
        confirm_export_btn = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.get_by_role("button", name="导 出")
        expect(confirm_export_btn).to_be_visible()

        # 执行导出下载，验证导出成功
        logger.info("点击确认导出，触发文件下载")
        with page.expect_download() as download_info:
            confirm_export_btn.click()
        download = download_info.value
        expect(page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame.locator("div").filter(has_text="导出成功").nth(3)).to_be_visible()
        
        logger.info("用例执行完成，物料清单导出成功")