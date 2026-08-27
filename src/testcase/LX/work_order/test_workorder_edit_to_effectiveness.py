import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.pages.LX.work_order.page_workorder_edit_to_effectiveness import WorkorderEditToEffectivenessPage
from src.data.LX.work_order.data_workorder_edit_to_effectiveness import *


class TestWorkorderEditToEffectiveness(BaseTest):
    """
    用例名：workorder_edit_to_effectiveness
    用例ms的id：100335
    """

    def test_workorder_edit_to_effectiveness(self, page: Page, project_name: str):
        f"""测试生产工单编辑到废弃功能
        用例名：workorder_edit_to_effectiveness
        用例ms的id：100335
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        try:
            logger.info("=" * 60)
            logger.info(f"开始执行workorder_edit_to_effectiveness")
            logger.info(f"用例ms的id：100335")
            logger.info("=" * 60)
            
            # 使用公用登录方法
            self.login(page, project_name)
            logger.info("登录成功，开始执行生产工单编辑到废弃流程")
            
            # 初始化页面对象
            wo_page = WorkorderEditToEffectivenessPage(page)
            
            # 导航到生产工单页面
            wo_page.navigate_to_workorder_page()
            
            # 获取iframe
            iframe = wo_page.get_workorder_iframe()
            
            # 点击新增按钮，获取新增弹窗页面对象
            add_modal_page = wo_page.click_add_button(iframe)
            
            # 填写新增工单信息
            copied_wo_no = wo_page.fill_add_workorder_info(add_modal_page)
            
            # 保存并关闭新增弹窗
            wo_page.save_and_close_add_modal(add_modal_page)
            
            # 粘贴工单号并查询
            wo_page.paste_and_query(iframe, copied_wo_no)
            
            # 选中工单并生效
            wo_page.select_and_effect(iframe)
            
            # 选中工单并废弃、取消
            wo_page.select_and_abandon_then_cancel(iframe)
            
            # 断言：验证取消操作执行成功
            logger.info("验证取消操作执行成功")
            # 验证页面仍能正常操作，没有错误提示
            assert iframe.get_by_role("button", name="查询").is_visible(), "页面操作失败，查询按钮不可见"
            logger.info("取消操作执行成功，页面正常，测试通过")
            
            logger.info("生产工单编辑到废弃流程执行完成！")
        except Exception as e:
            logger.error(f"测试执行失败: {str(e)}")
            raise
        finally:
            # 关闭当前页面
            page.close()