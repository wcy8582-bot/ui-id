from playwright.sync_api import Page
from src.common.logger import logger
from src.base.base_test import BaseTest
from src.pages.LX.work_order.page_workorder_approval_to_effectiveness import WorkorderApprovalToEffectivenessPage
from src.data.LX.work_order.data_workorder_approval_to_effectiveness import WorkorderApprovalToEffectivenessData


class TestWorkorderApprovalToEffectiveness(BaseTest):
    """
    用例名：workorder_approval_to_effectiveness
    用例ms的id：100336
    """

    def test_workorder_approval_to_effectiveness(self, page: Page, project_name: str):
        f"""测试工单审批至下发功能
        
        用例名：workorder_approval_to_effectiveness
        用例ms的id：100336
        
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        try:
            logger.info("=" * 60)
            logger.info(f"开始执行workorder_approval_to_effectiveness")
            logger.info(f"用例ms的id：100336")
            logger.info("=" * 60)
            
            # 使用公用登录方法
            self.login(page, project_name)
            
            # 初始化页面对象
            wo_page = WorkorderApprovalToEffectivenessPage(page)
            
            # 进入生产工单页面
            wo_page.navigate_to_workorder_page()
            
            # 获取主界面iframe
            main_iframe = wo_page.get_main_iframe()
            
            # 点击新增按钮，获取新增弹窗页
            add_popup = wo_page.click_add_button_get_popup(main_iframe)
            
            # 填写新增工单信息并复制工单号
            copied_workorder_no = wo_page.fill_add_workorder_form_and_copy_no(add_popup, WorkorderApprovalToEffectivenessData)
            
            # 提交审批并关闭弹窗
            wo_page.submit_approval_and_close_popup(add_popup)
            
            # 查询指定状态的工单
            wo_page.query_workorder(main_iframe, copied_workorder_no, WorkorderApprovalToEffectivenessData["status_edit"])
            
            # 工单生效
            wo_page.check_and_effect_workorder(main_iframe)
            
            # 工单下发
            wo_page.check_and_issue_workorder(main_iframe)
            
            logger.info("工单审批至下发测试执行完成！")
        except Exception as e:
            logger.error(f"工单审批至下发测试执行失败: {str(e)}")
            raise