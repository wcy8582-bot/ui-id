import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.pages.LX.work_order.page_workorder_edit_button import WorkorderEditButtonPage
from src.data.LX.work_order.data_workorder_edit_button import WorkorderEditButtonData


class TestWorkorderEditButton(BaseTest):
    """
    用例名：workorder_edit_button
    用例ms的id：100325
    """

    def test_workorder_edit_button(self, page: Page, project_name: str):
        f"""测试生产工单编辑按钮功能
        用例名：workorder_edit_button
        用例ms的id：100325
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        try:
            logger.info("=" * 60)
            logger.info(f"开始执行workorder_edit_button")
            logger.info(f"用例ms的id：100325")
            logger.info("=" * 60)
            
            # 使用公用登录方法
            self.login(page, project_name)
            
            # 初始化页面对象
            workorder_page = WorkorderEditButtonPage(page)
            
            # 进入生产工单页面
            workorder_page.navigate_to_workorder_page()
            
            # 获取主页面iframe
            main_iframe = workorder_page.get_main_iframe()
            
            # 点击新增按钮打开弹窗
            add_modal_page = workorder_page.click_add_button(main_iframe)
            
            # 填写新增工单信息
            workorder_page.fill_add_workorder_form(add_modal_page)
            
            # 保存工单并关闭弹窗
            workorder_page.save_and_close_modal(add_modal_page)
            
            # 查询已保存的工单
            workorder_page.search_workorder(main_iframe)
            
            # 选中工单并点击编辑按钮打开弹窗
            edit_modal_page = workorder_page.click_edit_button(main_iframe)
            
            # 关闭编辑弹窗
            workorder_page.close_modal(edit_modal_page)
            
            logger.info("测试执行成功！")
            
        except Exception as e:
            logger.error(f"测试执行失败: {str(e)}")
            raise
        finally:
            # 关闭主页面
            page.close()