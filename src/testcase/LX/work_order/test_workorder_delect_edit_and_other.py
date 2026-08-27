from playwright.sync_api import Page
import pytest
from src.common.logger import logger
from src.base.base_test import BaseTest
from src.pages.LX.work_order.page_workorder_delect_edit_and_other import WorkorderDelectEditAndOtherPage
from src.data.LX.work_order.data_workorder_delect_edit_and_other import WorkorderData
from src.common.tool import Tool


class TestWorkorderDelectEditAndOther(BaseTest):
    """
    用例名：workorder_delect_edit_and_other
    用例ms的id：100323
    """

    def test_workorder_other(self, page: Page, project_name: str):
        f"""测试工单相关操作功能
        
        用例名：workorder_delect_edit_and_other
        用例ms的id：100323
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        try:
            logger.info("=" * 60)
            logger.info(f"开始执行workorder_delect_edit_and_other")
            logger.info(f"用例ms的id：100322")
            logger.info("=" * 60)
            
            # 使用公用登录方法
            self.login(page, project_name)
            logger.info("登录成功，开始执行工单操作")
            
            # 初始化页面对象
            wo_page = WorkorderDelectEditAndOtherPage(page)
            
            # 进入生产工单页面
            wo_page.navigate_to_workorder_page()
            
            # 获取主页面iframe
            main_iframe = wo_page.get_main_iframe()
            
            # 新增第一个工单并保存
            modal1 = wo_page.click_add_button(main_iframe)
            wo_page.fill_workorder_modal(modal1, WorkorderData["order_no_1"], WorkorderData["plan_qty"])
            wo_page.click_save_button(modal1)
            modal1.close()
            logger.info("第一个工单保存成功")
            
            # 新增第二个工单并审批
            modal2 = wo_page.click_add_button(main_iframe)
            wo_page.fill_workorder_modal(modal2, WorkorderData["order_no_2"], WorkorderData["plan_qty"])
            wo_page.click_approve_button(modal2)
            modal2.close()
            logger.info("第二个工单审批成功")
            
            # 查询并勾选两个工单
            wo_page.click_query_button(main_iframe)
            wo_page.check_workorder_row(main_iframe, WorkorderData["order_no_2"])
            wo_page.check_workorder_row(main_iframe, WorkorderData["order_no_1"])
            logger.info("两个工单勾选成功")
            
            # 断言：验证删除按钮不可见
            logger.info("验证删除按钮不可点击")
            delete_button = main_iframe.get_by_role("button", name="删 除")
            
            # 检查按钮是否可见
            Tool.assert_button_disabled(delete_button, "删除按钮")
            
        except Exception as e:
            logger.error(f"测试执行失败: {str(e)}")
            raise