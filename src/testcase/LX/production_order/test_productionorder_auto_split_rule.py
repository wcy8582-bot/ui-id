import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool
from src.common.data_generator import DataGenerator

class TestProductionOrderAutoSplitRule(BaseTest):
    """
    用例名：productionorder_auto_split_rule
    用例ms的id：100111
    """

    def test_productionorder_auto_split_rule(self, page: Page, project_name: str):
        f"""测试生产订单自动拆分功能
        用例名：productionorder_auto_split_rule
        用例ms的id：100111
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：productionorder_auto_split_rule")
        logger.info(f"用例ms的id：100111")
        logger.info("=" * 60)
        
        # 使用公用登录方法登录系统
        logger.info("使用公用账号登录系统")
        self.login(page, project_name)
        
        # 进入生产订单模块
        logger.info("进入生产计划->生产订单模块")
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
        
        # 获取生产订单模块iframe上下文
        po_frame = page.locator("iframe[name=\"ProductionOrders\"]").content_frame
        
        # 输入目标订单号查询
        logger.info("查询目标测试订单")
        po_frame.get_by_role("textbox", name="订单号 :").fill(order_no)
        po_frame.get_by_role("button", name="查询").click()
        
        # 触发订单拆分流程
        logger.info("启动订单拆分流程")
        po_frame.get_by_label("", exact=True).check()
        po_frame.get_by_role("button", name="拆分").click()
        po_frame.get_by_role("button", name="search").click()
        
        # 选择目标产线
        logger.info("选择目标产线")
        line_select_frame = po_frame.locator("iframe").content_frame
        line_select_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        po_frame.get_by_label("车间/产线参照").get_by_role("button", name="确 定").click()
        
        # 第一次自动拆分：校验未填产能提示
        logger.info("执行第一次自动拆分")
        po_frame.get_by_role("button", name="自动拆分").click()
        expect(po_frame.locator("body")).to_contain_text("请先填写产线产能")
        logger.info("校验通过：未填写产能时正确弹出提示")
        
        # 填写产能后再次执行自动拆分
        logger.info("填写产线产能")
        line_output = DataGenerator.generate_random_decimal(3, 2)
        po_frame.get_by_role("spinbutton", name="产线产能").fill(str(line_output))
        po_frame.get_by_role("button", name="自动拆分").click()

        # 计算拆分订单总数量
        logger.info("计算拆分订单总数量")
        all_order_num = 0
        order_count = Tool.split_order_count(1000, line_output)
        for i in range(order_count):
            j = i + 2
            quantity_value = po_frame.get_by_role("spinbutton").nth(j).get_attribute("value")
            logger.info(f"拆分数量值: {quantity_value}")
            all_order_num += float(quantity_value)

        assert all_order_num == 1000, f"拆分数量不是1000: {all_order_num}"
        logger.info("校验通过：拆分数量总和等于1000")
        
        # 删除拆分结果，校验清空
        logger.info("执行拆分结果删除操作")
        po_frame.get_by_role("dialog", name="订单拆分").get_by_label("Select all").check()
        po_frame.get_by_label("订单拆分").get_by_role("button", name="删 除").click()
        expect(po_frame.get_by_label("订单拆分").locator("tbody")).to_contain_text("暂无数据")
        
        logger.info(f"用例productionorder_auto_split_rule执行完成")