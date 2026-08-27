import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestVerifyExportPerformance(BaseTest):
    """
    用例名：verify_export_performance
    用例ms的id：101300
    """

    def test_verify_export_performance(self, page: Page, project_name: str):
        f"""测试物料清单导出功能
        用例名：verify_export_performance
        用例ms的id：101300
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_export_performance")
        logger.info(f"用例ms的id：101300")
        logger.info("=" * 60)
        
        # 调用公用登录方法完成登录
        logger.info("登录系统")
        self.login(page, project_name)
        
        # 导航进入物料清单页面
        logger.info("进入物料清单菜单")
        page.get_by_text("基础资料").click()
        page.get_by_text("物料清单").click()
        
        # 获取内容iframe，简化后续定位
        content_iframe = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 打开导出配置弹窗
        logger.info("打开导出配置弹窗")
        expect(content_iframe.get_by_role("button", name="export 导出")).to_be_visible()
        content_iframe.get_by_role("button", name="export 导出").click()
        expect(content_iframe.get_by_text("文件名：导出数据范围：选中页面范围全部数据 — （请输入页码范围（例如：1-3））")).to_be_visible()
        content_iframe.locator("div").filter(has_text="文件名：导出数据范围：选中页面范围全部数据 — （请输入页码范围（例如：1-3））").nth(5).click()
        
        # 配置导出参数
        logger.info("配置导出参数")
        content_iframe.get_by_role("radio", name="选中页面范围").check()
        content_iframe.get_by_role("spinbutton").nth(1).click()
        expect(content_iframe.get_by_text("文件名：导出数据范围：选中页面范围全部数据 — （请输入页码范围（例如：1-3））")).to_be_visible()
        
        # 触发导出并等待下载
        logger.info("触发导出操作，等待下载完成")
        with page.expect_download() as download_info:
            content_iframe.get_by_role("button", name="导 出").click()
        download = download_info.value
        
        # 断言导出成功
        logger.info("断言导出成功提示")
        expect(content_iframe.locator("div").filter(has_text="导出成功").nth(3)).to_be_visible()
        
        logger.info(f"用例verify_export_performance执行完成")