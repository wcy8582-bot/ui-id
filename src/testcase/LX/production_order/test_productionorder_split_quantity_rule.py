import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool
from src.common.data_generator import DataGenerator



class TestProductionOrderSplitQuantityRule(BaseTest):
    """
    用例名：productionorder_split_quantity_rule
    用例ms的id：100113
    """

    def test_productionorder_split_quantity_rule(self, page: Page, project_name: str):
        f"""测试生产订单拆分数量规则校验
        用例名：productionorder_split_quantity_rule
        用例ms的id：100113
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行测试用例：productionorder_split_quantity_rule")
        logger.info(f"用例ms ID：100113")
        logger.info("=" * 60)
        
        # 使用封装好的公用登录方法登录
        logger.info("登录系统")
        self.login(page, project_name)
        
        # 导航到生产订单页面
        logger.info("导航到生产订单模块")
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
        
        # 获取生产订单iframe上下文，简化后续代码
        po_frame = page.locator("iframe[name=\"ProductionOrders\"]").content_frame
        
        # 查询目标订单
        logger.info("查询指定订单号的生产订单")
        po_frame.get_by_role("textbox", name="订单号 :").click()
        po_frame.get_by_role("textbox", name="订单号 :").fill(order_no)
        po_frame.get_by_role("textbox", name="订单号 :").press("Enter")
        po_frame.get_by_role("button", name="查询").click()
        
        # 进入拆分流程
        logger.info("勾选订单，打开拆分弹窗")
        po_frame.get_by_label("", exact=True).check()
        po_frame.get_by_role("button", name="拆分").click()
        
        # 校验产线产能输入负数的错误提示
        logger.info("校验产线产能负数输入规则")
        po_frame.get_by_role("spinbutton", name="产线产能").click()
        po_frame.get_by_role("spinbutton", name="产线产能").fill("-1")
        po_frame.get_by_text("产线产能", exact=True).click()
        expect(po_frame.locator("#productionCapacity_help")).to_contain_text("产线产能不能小于0")
        
        # 测试自动拆分的小数保留规则
        logger.info("测试自动拆分后小数保留规则")
        line_output = DataGenerator.generate_random_decimal(3, 7)
        po_frame.get_by_role("spinbutton", name="产线产能").click()
        po_frame.get_by_role("spinbutton", name="产线产能").fill(str(line_output))
        po_frame.get_by_text("产线产能").click()
        po_frame.get_by_role("button", name="自动拆分").click()
        
        # 断言拆分结果符合保留6位小数的规则
        logger.info("验证拆分结果的小数位数")
        
        # 获取三个输入框的值
        capacity_value = po_frame.get_by_role("spinbutton", name="产线产能").get_attribute("value")
        
        order_count = Tool.split_order_count(1000, int(line_output))
        for i in range(order_count):
            j = i + 2
            quantity_value = po_frame.get_by_role("spinbutton").nth(j).get_attribute("value")
            logger.info(f"拆分数量值: {quantity_value}")
            assert Tool.check_decimal_places(quantity_value, 6), f"拆分数量不是6位小数: {quantity_value}"
        
        logger.info(f"产线产能值: {capacity_value}")
        
        # 验证小数位数是否为6位
        assert Tool.check_decimal_places(capacity_value, 6), f"产线产能不是6位小数: {capacity_value}"
        
        logger.info("验证通过：所有值均为6位小数")
        
        # 校验拆分行数量输入负数的规则
        logger.info("校验拆分行数量负数输入规则")
        po_frame.get_by_role("spinbutton").nth(2).click()
        po_frame.get_by_role("spinbutton").nth(2).press("ArrowRight")
        po_frame.get_by_role("spinbutton").nth(2).fill("-1")
        po_frame.get_by_text("拆分数量", exact=True).click()
        expect(po_frame.get_by_role("spinbutton").nth(2)).to_have_value("0")
        
        logger.info("测试用例执行完成")