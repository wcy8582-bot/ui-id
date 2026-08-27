import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestWorkOrderListToPage(BaseTest):
    """
    用例名：workorder_list_to_page
    用例ms的id：100300
    """

    def test_workorder_list_to_page(self, page: Page, project_name: str):
        f"""测试生产工单列表跳转页码功能
        用例名：workorder_list_to_page
        用例ms的id：100300
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_list_to_page")
        logger.info(f"用例ms的id：100300")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 操作生产工单iframe内的分页组件
        logger.info("操作生产工单iframe内的分页组件")
        workorder_frame = page.locator("iframe[name=\"WorkOrder\"]").content_frame
        workorder_frame.get_by_text("条/页").click()
        workorder_frame.get_by_text("10 条/页").click()
        
        # 等待页面加载完成
        page.wait_for_load_state("networkidle")
        
        # 输入页码3并按Enter
        logger.info("输入页码3并跳转")
        page_input = workorder_frame.get_by_role("textbox", name="页")
        page_input.click()
        page_input.fill("3")
        page_input.press("Enter")
        
        # 等待页面加载完成
        page.wait_for_load_state("networkidle")
        
        # 验证跳转成功
        logger.info("验证跳转成功")
        
        # 1. 验证第三页按钮被激活
        active_page = workorder_frame.locator(".ant-pagination-item-active")
        active_title = active_page.get_attribute("title")
        assert active_title == "3", f"当前激活的页码是 {active_title}，不是第三页"
        logger.info("验证通过：成功跳转到第三页")
        
        # 2. 验证表格数据
        table_body = workorder_frame.locator("tbody.ant-table-tbody")
        first_row_key = table_body.locator("tr.ant-table-row.ant-table-row-level-0").first.get_attribute("data-row-key")
        logger.info(f"第三页第一行的data-row-key: {first_row_key}")
        assert first_row_key is not None, "无法获取第三页第一行的data-row-key"
        logger.info("验证通过：表格数据正常显示")
        
        # 3. 验证分页信息
        try:
            page_info = workorder_frame.locator(".ant-pagination-info").text_content(timeout=1000)
            if page_info:
                logger.info(f"分页信息: {page_info}")
            else:
                logger.info("未找到分页信息")
        except Exception as e:
            logger.warning(f"获取分页信息失败: {str(e)}")
        
        # 关闭页面
        logger.info("关闭当前测试页面")
        page.close()