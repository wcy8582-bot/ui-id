import pytest
from playwright.sync_api import Page
from src.common.logger import logger
from src.base.base_test import BaseTest
from src.pages.LX.work_order.page_workorder_fuzzy_query import WorkorderFuzzyQueryPage
from src.data.LX.work_order.data_workorder_fuzzy_query import *


class TestWorkorderFuzzyQuery(BaseTest):
    """
    用例名：workorder_fuzzy_query
    用例ms的id：100727
    """

    def test_workorder_fuzzy_query(self, page: Page, project_name: str):
        f"""测试生产工单模糊查询功能
        用例名：workorder_fuzzy_query
        用例ms的id：100727
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_fuzzy_query")
        logger.info(f"用例ms的id：100727")
        logger.info("=" * 60)
        
        try:
            # 使用公用登录方法
            self.login(page, project_name)
            
            # 初始化页面对象
            workorder_page = WorkorderFuzzyQueryPage(page)
            
            # 进入生产工单页面
            workorder_page.navigate_to_workorder_page()
            
            # 获取生产工单iframe
            iframe = workorder_page.get_workorder_iframe()
            
            # 点击新增按钮，创建测试工单
            add_modal = workorder_page.click_add_button(iframe)
            workorder_page.fill_workorder_form(add_modal)
            workorder_page.save_workorder(add_modal)
            
            # 工单号模糊查询
            workorder_page.fuzzy_query_by_field(iframe, "工单号", WorkorderData["work_order_id_fuzzy"])
            workorder_page.view_workorder(iframe)
            
            # 重置查询条件
            workorder_page.reset_query(iframe)
            
            # 产品编码模糊查询
            workorder_page.fuzzy_query_by_field(iframe, "产品编码", WorkorderData["product_code_fuzzy"])
            workorder_page.view_workorder_detail(iframe, WorkorderData["detail_url"])
            
            # 重置查询条件
            workorder_page.reset_query(iframe)
            
            # 产品名称模糊查询
            workorder_page.fuzzy_query_by_field(iframe, "产品名称", WorkorderData["product_name_error"])
            workorder_page.clear_field(iframe, "产品名称")
            workorder_page.fuzzy_query_by_field(iframe, "产品名称", WorkorderData["product_name_fuzzy"])
            workorder_page.view_workorder_detail(iframe, WorkorderData["detail_url"])
            
            # 重置查询条件
            workorder_page.reset_query(iframe)
            
            # 生产批号模糊查询
            workorder_page.fuzzy_query_by_field(iframe, "生产批号", WorkorderData["batch_no_fuzzy"])
            workorder_page.view_workorder_detail(iframe, WorkorderData["detail_url"])
            
            logger.info("测试执行成功！")
            
        except Exception as e:
            logger.error(f"测试执行失败: {str(e)}")
            raise
        finally:
            # 关闭主页面
            logger.info("关闭主页面，用例执行完毕")
            page.close()