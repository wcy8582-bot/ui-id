import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool
from src.common.data_generator import DataGenerator

class TestProductionOrderAutoSplitDateRule(BaseTest):
    """
    用例名：productionorder_auto_split_date_rule
    用例ms的id：100115
    """

    def test_productionorder_auto_split_date_rule(self, page: Page, project_name: str):
        f"""测试生产订单自动拆分日期规则
        用例名：productionorder_auto_split_date_rule
        用例ms的id：100115
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行测试用例：productionorder_auto_split_date_rule")
        logger.info(f"用例ms ID：100115")
        logger.info("=" * 60)
        
        # 使用公用登录方法登录系统
        logger.info("调用公用登录方法登录系统")
        self.login(page, project_name)

        # 进入生产计划-生产订单页面
        logger.info("进入生产计划模块，打开生产订单页面")
        page.get_by_role("listitem", name="生产计划").click()
        page.get_by_text("生产订单").click()

        # 创建测试订单
        order_no = Tool.create_production_order(page, "1000", "测试订单")
        if order_no:
            logger.info(f"生产订单创建成功: {order_no}")
        else:
            logger.error("创建生产订单失败")
            # 用例直接失败，不继续后续步骤
            pytest.fail("创建生产订单失败")


        # 获取生产订单iframe上下文，简化重复定位
        po_frame = page.locator("iframe[name=\"ProductionOrders\"]").content_frame
        logger.info("获取生产订单页面iframe成功，开始查询目标订单")

        # 输入订单号查询目标订单
        po_frame.get_by_role("textbox", name="订单号 :").click()
        po_frame.get_by_role("textbox", name="订单号 :").fill(order_no)
        po_frame.get_by_role("button", name="查询").click()

        # 选中订单发起拆分
        logger.info("查询完成，选中目标订单发起拆分")
        po_frame.get_by_label("", exact=True).check()
        po_frame.get_by_role("button", name="拆分").click()

        page_msg = Tool.get_split_order_info(page)
        logger.info(page_msg)
        if page_msg["order_no"] is None:
            logger.error("获取拆分单据基础信息失败")
            # 用例直接失败，不继续后续步骤
            pytest.fail("获取拆分单据基础信息失败")

        # 选择目标产线
        logger.info("打开产线选择弹窗，选择目标产线")
        po_frame.get_by_role("button", name="search").click()
        inner_search_frame = po_frame.locator("iframe").content_frame
        inner_search_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        po_frame.get_by_label("车间/产线参照").get_by_role("button", name="确 定").click()

        # 设置产线产能，点击自动拆分
        logger.info("设置产线产能为500，点击自动拆分")
        po_frame.get_by_role("spinbutton", name="产线产能").click()
        po_frame.get_by_role("spinbutton", name="产线产能").fill("500")
        po_frame.get_by_role("button", name="自动拆分").click()

        # 验证默认拆分日期
        logger.info("验证自动拆分后默认日期是否正确")
        expect(po_frame.get_by_role("textbox", name="请选择日期").first).to_have_value(page_msg["plan_start_time"])

        # 测试第一个范围外日期：2026-04-13
        logger.info("测试范围外日期的校验提示")
        left_date = DataGenerator().get_random_start_date(page_msg["plan_start_time"])
        logger.info(f"随机生成的开始日期: {left_date}")
        po_frame.get_by_role("textbox", name="请选择日期").first.click()
        po_frame.get_by_role("button", name="close-circle").nth(1).click()
        po_frame.get_by_label("确认").get_by_role("button", name="确 定").click()
        po_frame.get_by_role("textbox", name="请选择日期").first.fill(left_date)
        po_frame.get_by_text("订单拆分").click()
        expect(po_frame.get_by_label("确认")).to_contain_text("选择的日期在订单的开始结束范围外，确认选择该日期么？")
        po_frame.get_by_label("确认").get_by_role("button", name="确 定").click()

        # 测试第二个范围外日期：2026-04-30
        logger.info("测试范围外日期")
        right_date = DataGenerator().get_random_end_date(page_msg["plan_end_time"])
        logger.info(f"随机生成的结束日期: {right_date}")
        po_frame.get_by_role("textbox", name="请选择日期").first.click()
        po_frame.get_by_role("button", name="close-circle").nth(1).click()
        po_frame.get_by_label("确认").get_by_role("button", name="确 定").click()
        po_frame.get_by_role("textbox", name="请选择日期").first.click()
        po_frame.get_by_role("textbox", name="请选择日期").first.fill(right_date)
        po_frame.get_by_text("订单拆分").click()
        expect(po_frame.get_by_label("确认")).to_contain_text("选择的日期在订单的开始结束范围外，确认选择该日期么？")
        po_frame.get_by_label("确认").get_by_role("button", name="确 定").click()

        logger.info("测试用例productionorder_auto_split_date_rule执行完成")