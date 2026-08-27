import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestWorkOrderListPageNum(BaseTest):
    """
    用例名：workorder_list_page_num
    用例ms的id：100296
    """

    def test_workorder_list_page_num(self, page: Page, project_name: str):
        f"""测试生产工单列表页页码功能
        用例名：workorder_list_page_num
        用例ms的id：100296
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_list_page_num")
        logger.info(f"用例ms的id：100296")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 操作生产工单列表页页码
        logger.info("操作生产工单列表页页码")
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("cell", name="20", exact=True).click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_text("条/页").click()
        page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_text("10 条/页").click()
        
        # 等待页面加载完成
        page.wait_for_load_state("networkidle")
        
        # 验证列表显示效果是否正确变化
        logger.info("验证列表显示效果")
        workorder_frame = page.locator("iframe[name=\"WorkOrder\"]").content_frame
        
        # 定位表格主体
        table_body = workorder_frame.locator("tbody.ant-table-tbody")
        
        # 计算数据行数（排除隐藏的测量行）
        data_rows = table_body.locator("tr.ant-table-row.ant-table-row-level-0").all()
        row_count = len(data_rows)
        logger.info(f"当前显示的工单行数: {row_count}")
        
        # 断言行数不超过10条
        assert row_count <= 10, f"切换到10条/页后，显示了 {row_count} 行，超过了10条"
        logger.info("验证通过：行数不超过10条")
        
        # 验证分页信息是否显示正确
        try:
            page_info = workorder_frame.locator(".ant-pagination-info").text_content(timeout=1000)
            if page_info:
                logger.info(f"分页信息: {page_info}")
            else:
                logger.info("未找到分页信息")
        except Exception as e:
            logger.warning(f"获取分页信息失败: {str(e)}")

        # 关闭页面
        logger.info("测试完成，关闭页面")
        page.close()