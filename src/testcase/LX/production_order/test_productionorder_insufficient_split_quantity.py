import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool
from src.common.data_generator import DataGenerator

class TestProductionOrderInsufficientSplitQuantity(BaseTest):
    """
    用例名：productionorder_insufficient_split_quantity
    用例ms的id：100104
    """

    def test_productionorder_insufficient_split_quantity(self, page: Page, project_name: str):
        f"""测试生产订单剩余可拆分数量不足拆分场景
        用例名：productionorder_insufficient_split_quantity
        用例ms的id：100104
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行测试用例：productionorder_insufficient_split_quantity")
        logger.info(f"用例ms的id：100104")
        logger.info("=" * 60)
        
        # 使用公用登录方法登录系统
        logger.info("登录系统")
        self.login(page, project_name)
        
        # 进入生产订单模块
        logger.info("进入生产计划->生产订单页面")
        page.get_by_role("listitem", name="生产计划").click()
        page.get_by_text("生产订单").click()

        order_no = Tool.create_production_order(page, "100", "测试订单")
        if order_no:
            logger.info(f"生产订单创建成功: {order_no}")
        else:
            logger.error("创建生产订单失败")
            # 用例直接失败，不继续后续步骤
            pytest.fail("创建生产订单失败")
        
        # 提取生产订单iframe，简化后续调用
        order_iframe = page.locator("iframe[name=\"ProductionOrders\"]").content_frame
        
        # 查询目标生产订单
        logger.info("输入订单号查询目标订单")
        order_iframe.get_by_role("textbox", name="订单号 :").click()
        order_iframe.get_by_role("textbox", name="订单号 :").fill(order_no)
        order_iframe.get_by_role("button", name="查询").click()
        
        # 发起拆分，新增拆分行
        logger.info("勾选订单，发起拆分操作，新增拆分行")
        order_iframe.get_by_label("", exact=True).check()
        order_iframe.get_by_role("button", name="拆分").click()
        order_iframe.get_by_role("button", name="增 行").click()
        
        # 填写拆分信息，去除录制产生的多余CapsLock按键操作
        logger.info("填写拆分行信息")
        order_iframe.locator(".ant-table-cell > .ant-input").first.click()
        order_iframe.locator(".ant-table-cell > .ant-input").first.fill(DataGenerator().get_order_no("SCDD"))
        order_iframe.get_by_role("spinbutton").nth(2).click()
        order_iframe.get_by_role("spinbutton").nth(2).fill("100")
        order_iframe.get_by_role("button", name="确 定").click()
        
        # 再次查询发起拆分，验证错误提示
        logger.info("再次查询后发起拆分，验证错误提示")
        order_iframe.get_by_role("button", name="查询").click()
        order_iframe.get_by_role("button", name="拆分").click()
        
        # 断言提示信息符合预期
        logger.info("断言错误提示信息正确")
        expect(order_iframe.locator("body")).to_contain_text("该生产订单剩余可拆分数量为0，不允许拆分！")
        logger.info("测试用例执行完成")