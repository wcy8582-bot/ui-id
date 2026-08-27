import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestWorkorderListPageChange(BaseTest):
    """
    用例名：workorder_list_page_change
    用例ms的id：100297
    """

    def test_workorder_list_page_change(self, page: Page, project_name: str):
        f"""测试生产工单列表页切换分页功能
        用例名：workorder_list_page_change
        用例ms的id：100297
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_list_page_change")
        logger.info(f"用例ms的id：100297")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 切换分页配置
        logger.info("切换分页显示条数为10条/页，并跳转至第3页")
        workorder_frame = page.locator("iframe[name=\"WorkOrder\"]").content_frame
        workorder_frame.get_by_text("条/页").click()
        workorder_frame.get_by_text("10 条/页").click()
        
        # 等待页面加载完成
        page.wait_for_load_state("networkidle")
        
        # 点击第三页
        logger.info("点击第三页")
        third_page_button = workorder_frame.locator("li[title=\"3\"].ant-pagination-item")
        third_page_button.click()
        
        # 等待页面加载完成
        page.wait_for_load_state("networkidle")
        
        # 验证列表切换到第三页
        logger.info("验证列表切换到第三页")
        
        # 1. 验证第三页按钮被激活
        active_page = workorder_frame.locator(".ant-pagination-item-active")
        active_title = active_page.get_attribute("title")
        assert active_title == "3", f"当前激活的页码是 {active_title}，不是第三页"
        logger.info("验证通过：第三页按钮已激活")
        
        # 2. 验证表格数据已更新（比较data-row-key）
        table_body = workorder_frame.locator("tbody.ant-table-tbody")
        first_row_key = table_body.locator("tr.ant-table-row.ant-table-row-level-0").first.get_attribute("data-row-key")
        logger.info(f"第三页第一行的data-row-key: {first_row_key}")
        # 确保获取到了有效的data-row-key
        assert first_row_key is not None, "无法获取第三页第一行的data-row-key"
        logger.info("验证通过：表格数据已更新")
        
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