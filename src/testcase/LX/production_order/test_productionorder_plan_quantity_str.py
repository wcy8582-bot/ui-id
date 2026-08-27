import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.data_generator import DataGenerator


class TestProductionOrderPlanQuantityCheck(BaseTest):
    """
    用例名：productionorder_plan_quantity_str
    用例ms的id：100096
    """

    def test_productionorder_plan_quantity_str(self, page: Page, project_name: str):
        f"""测试生产订单计划数量非法输入校验功能
        用例名：productionorder_plan_quantity_str
        用例ms的id：100096
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：productionorder_plan_quantity_str")
        logger.info(f"用例ms的id：100096")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法
        self.login(page, project_name)
        
        # 进入生产订单页面
        logger.info("进入生产计划模块，打开生产订单页面")
        page.get_by_role("listitem", name="生产计划").click()
        page.get_by_text("生产订单").click()
        
        # 获取iframe内容上下文
        order_frame = page.locator("iframe[name=\"ProductionOrders\"]").content_frame
        
        # 打开新增生产订单弹窗
        logger.info("点击新增按钮，打开新增生产订单弹窗")
        order_frame.get_by_role("button", name="新 增").click()
        
        # 计划数量输入框输入非法特殊字符
        logger.info("在*计划数量输入框输入特殊字符@@@@")
        order_frame.get_by_role("spinbutton", name="* 计划数量").click()
        generator = DataGenerator()
        test_str = generator.get_random_string(5)
        logger.info(f"输入特殊字符：{test_str}")
        order_frame.get_by_role("spinbutton", name="* 计划数量").fill(test_str)
        
        # 点击空白处触发校验
        logger.info("触发前端校验，检查错误提示信息")
        order_frame.get_by_text("新增生产订单").click()
        
        # 断言错误提示符合预期
        expect(order_frame.locator("#planNum_help")).to_contain_text("请输入计划数量")
        logger.info("断言通过，用例执行完成")