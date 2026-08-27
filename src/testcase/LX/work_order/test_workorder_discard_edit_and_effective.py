from playwright.sync_api import Page
import pytest
from src.common.logger import logger
from src.base.base_test import BaseTest
from src.pages.LX.work_order.page_workorder_discard_edit_and_effective import WorkorderDiscardEditAndEffectivePage
from src.data.LX.work_order.data_workorder_discard_edit_and_effective import *


class TestWorkorderDiscardEditAndEffective(BaseTest):
    """
    用例名：workorder_discard_edit_and_effective
    用例ms的id：100387
    功能：测试工单新增、生效功能
    """

    def test_workorder_discard_edit_and_effective(self, page: Page, project_name: str):
        f"""测试工单新增、保存、生效、勾选的完整流程
        用例名：workorder_discard_edit_and_effective
        用例ms的id：100387
        项目名：{project_name}
        
        Args:
            page: Playwright页面实例
            project_name: 测试项目名称
        """
        try:
            logger.info("=" * 60)
            logger.info(f"开始执行workorder_discard_edit_and_effective")
            logger.info(f"用例ms的id：100387")
            logger.info("=" * 60)
            
            # 使用公用登录方法
            self.login(page, project_name)
            logger.info("公用登录成功")
            
            # 初始化页面对象
            workorder_page = WorkorderDiscardEditAndEffectivePage(page)
            
            # 导航到生产工单页面
            workorder_page.navigate_to_workorder_page()
            
            # 获取生产工单主iframe
            iframe = workorder_page.get_main_iframe()
            
            # 新增第一个工单并保存
            workorder_page.create_and_save_workorder(
                iframe, 
                WorkorderData["workorder_no_1"], 
                WorkorderData["material_row_name"], 
                WorkorderData["svg_material_index"], 
                WorkorderData["div_second_select_index"], 
                WorkorderData["plan_qty"]
            )
            logger.info("第一个工单新增并保存成功")
            
            # 新增第二个工单并生效
            workorder_page.create_and_effective_workorder(
                iframe, 
                WorkorderData["workorder_no_2"], 
                WorkorderData["material_row_name"], 
                WorkorderData["svg_material_index"], 
                WorkorderData["div_second_select_index"], 
                WorkorderData["plan_qty"]
            )
            logger.info("第二个工单新增并生效成功")
            
            # 勾选新增的两个工单
            workorder_page.check_two_workorders(iframe, WorkorderData["row_no_2"], WorkorderData["row_no_1"], WorkorderData["workorder_no_2"], WorkorderData["workorder_no_1"])
            logger.info("两个新增工单勾选成功")

            # 断言，废弃按钮置灰
            workorder_page.assert_discard_button_disabled(iframe)
            
            logger.info("=" * 60)
            logger.info("workorder_discard_edit_and_effective执行完成")
            logger.info("=" * 60)
            
        except Exception as e:
            logger.error(f"测试执行失败: {str(e)}")
            raise