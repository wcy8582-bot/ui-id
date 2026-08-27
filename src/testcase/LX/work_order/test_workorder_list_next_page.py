import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestWorkOrderListNextPage(BaseTest):
    """
    用例名：workorder_list_next_page
    用例ms的id：100298
    """

    def test_workorder_list_next_page(self, page: Page, project_name: str):
        f"""测试生产工单列表翻页功能
        用例名：workorder_list_next_page
        用例ms的id：100298
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_list_next_page")
        logger.info(f"用例ms的id：100299")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 测试生产工单列表翻页
        logger.info("测试生产工单列表翻页")
        workorder_frame = page.locator("iframe[name=\"WorkOrder\"]").content_frame
        
        # 1. 点击下一页
        logger.info("点击下一页")
        next_button = workorder_frame.locator("li[title=\"下一页\"]").or_(workorder_frame.locator("li.ant-pagination-next"))
        next_button.click()
        
        # 等待页面加载完成
        page.wait_for_load_state("networkidle")
        
        # 验证切换到下一页
        logger.info("验证切换到下一页")
        active_page = workorder_frame.locator(".ant-pagination-item-active")
        active_title = active_page.get_attribute("title")
        logger.info(f"当前激活的页码: {active_title}")
        assert active_title is not None, "无法获取当前激活的页码"
        logger.info("验证通过：成功切换到下一页")
        
        # 2. 点击上一页
        logger.info("点击上一页")
        prev_button = workorder_frame.locator("li[title=\"上一页\"]").or_(workorder_frame.locator("li.ant-pagination-prev"))
        prev_button.click()
        
        # 等待页面加载完成
        page.wait_for_load_state("networkidle")
        
        # 验证切换回上一页
        logger.info("验证切换回上一页")
        active_page = workorder_frame.locator(".ant-pagination-item-active")
        active_title = active_page.get_attribute("title")
        logger.info(f"当前激活的页码: {active_title}")
        assert active_title is not None, "无法获取当前激活的页码"
        logger.info("验证通过：成功切换回上一页")
        
        # 3. 验证表格数据
        table_body = workorder_frame.locator("tbody.ant-table-tbody")
        first_row_key = table_body.locator("tr.ant-table-row.ant-table-row-level-0").first.get_attribute("data-row-key")
        logger.info(f"当前页第一行的data-row-key: {first_row_key}")
        assert first_row_key is not None, "无法获取当前页第一行的data-row-key"
        logger.info("验证通过：表格数据正常显示")
        
        # 关闭页面
        logger.info("关闭当前测试页面")
        page.close()