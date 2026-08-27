import pytest
from playwright.sync_api import Page, expect
from src.common.logger import logger
from src.base.base_test import BaseTest
from src.pages.LX.work_order.page_workorder_new_page import PageWorkorderNewPage
from src.data.LX.work_order.data_workorder_new_page import *


class TestWorkorderNewPage(BaseTest):
    """
    用例名：workorder_new_page
    用例ms的id：100403
    """

    def test_workorder_new_page(self, page: Page, project_name: str):
        f"""测试生产工单新增弹窗功能
        用例名：workorder_new_page
        用例ms的id：100403
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        try:
            logger.info("=" * 60)
            logger.info("开始执行生产工单新增弹窗测试")
            logger.info(f"用例ms的id：100403")
            logger.info("=" * 60)
            
            # 使用公用登录方法
            self.login(page, project_name)
            logger.info("登录成功")
            
            # 初始化页面对象
            workorder_page = PageWorkorderNewPage(page)
            
            # 导航到生产工单页面
            workorder_page.navigate_to_workorder_page()
            
            # 获取新增弹窗
            popup_page = workorder_page.click_add_button_and_get_popup()
            
            # 断言：验证弹窗是否成功打开
            assert popup_page is not None, "新增弹窗未打开"
            assert not popup_page.is_closed(), "新增弹窗已关闭"
            logger.info(f"新增弹窗成功打开，URL: {popup_page.url}")
            
            # 关闭新增弹窗
            workorder_page.close_popup(popup_page)
            
            logger.info("生产工单新增弹窗测试执行完成！")
            
        except Exception as e:
            logger.error(f"测试执行失败: {str(e)}")
            raise
        finally:
            # 关闭主页面（保持原逻辑）
            if not page.is_closed():
                page.close()