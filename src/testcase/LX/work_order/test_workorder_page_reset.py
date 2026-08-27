import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool

class TestWorkorderPageReset(BaseTest):
    """
    用例名：workorder_page_reset
    用例ms的id：100191
    """

    def test_workorder_page_reset(self, page: Page, project_name: str):
        f"""测试生产工单重置功能
        用例名：workorder_page_reset
        用例ms的id：100191
        项目名：LX
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_page_reset")
        logger.info(f"用例ms的id：100191")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 获取workorder_frame
        workorder_frame = page.locator("iframe[name=\"WorkOrder\"]").content_frame
        
        # 获取初始数据总数
        logger.info("获取初始数据总数")
        initial_total = workorder_frame.locator(".ant-pagination-total-text").text_content()
        logger.info(f"初始数据总数: {initial_total}")
        
        # 执行生产工单页面查询操作
        logger.info("执行生产工单页面查询操作")
        Tool.select_workorder_types(page, "生效")
        workorder_frame.locator("form").get_by_text("工单状态").click()
        workorder_frame.get_by_role("button", name="查询").click()
        
        # 等待页面加载完成
        page.wait_for_load_state("networkidle")
        
        # 获取查询后数据总数
        logger.info("获取查询后数据总数")
        filtered_total = workorder_frame.locator(".ant-pagination-total-text").text_content()
        logger.info(f"查询后数据总数: {filtered_total}")
        
        # 验证查询后数据数量减少
        assert filtered_total != initial_total, "查询后数据数量未变化"
        logger.info("验证通过：查询后数据数量减少")
        
        # 点击重置按钮
        logger.info("点击重置按钮")
        workorder_frame.get_by_role("button", name="重置").click()
        
        # 等待页面加载完成
        page.wait_for_load_state("networkidle")
        
        # 验证重置结果
        logger.info("验证重置后数据总数")
        reset_total = workorder_frame.locator(".ant-pagination-total-text").text_content()
        logger.info(f"重置后数据总数: {reset_total}")
        
        # 验证重置后数据数量恢复
        assert reset_total == initial_total, f"重置后数据数量未恢复，初始: {initial_total}, 重置后: {reset_total}"
        logger.info("验证通过：重置后数据数量恢复")
        
        page.close()