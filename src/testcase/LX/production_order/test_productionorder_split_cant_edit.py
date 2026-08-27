import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool
from src.common.data_generator import DataGenerator

class TestProductionOrderSplitCantEdit(BaseTest):
    """
    用例名：productionorder_split_cant_edit
    用例ms的id：100087
    """

    def test_productionorder_split_cant_edit(self, page: Page, project_name: str):
        f"""测试生产订单拆分后不可编辑功能
        用例名：productionorder_split_cant_edit
        用例ms的id：100087
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行测试用例：productionorder_split_cant_edit")
        logger.info(f"用例ms ID：100087")
        logger.info("=" * 60)

        # 调用公用登录方法登录系统
        logger.info("登录系统")
        self.login(page, project_name)

        # 进入生产订单模块
        logger.info("进入生产订单页面")
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

        # 提取生产订单iframe，简化后续定位
        prod_order_frame = page.locator("iframe[name=\"ProductionOrders\"]").content_frame

        # 查询目标订单
        logger.info("查询目标生产订单")
        prod_order_frame.get_by_role("textbox", name="订单号 :").click()
        prod_order_frame.get_by_role("textbox", name="订单号 :").fill(order_no)
        prod_order_frame.get_by_role("button", name="查询").click()

        # 执行订单拆分操作
        logger.info("执行生产订单拆分")
        batch_no = DataGenerator().get_order_no("SCPH")
        logger.info(f"生成的批次号: {batch_no}")
        prod_order_frame.get_by_label("", exact=True).check()
        prod_order_frame.get_by_role("button", name="拆分").click()
        prod_order_frame.get_by_role("button", name="增 行").click()
        prod_order_frame.locator(".ant-table-cell > .ant-input").first.click()
        prod_order_frame.locator(".ant-table-cell > .ant-input").first.fill(batch_no)
        prod_order_frame.get_by_role("spinbutton").nth(2).click()
        prod_order_frame.get_by_role("spinbutton").nth(2).fill("500")
        prod_order_frame.get_by_role("button", name="确 定").click()

        # 验证拆分后不可编辑
        logger.info("验证拆分后编辑提示信息")
        prod_order_frame.get_by_role("button", name="查询").click()
        prod_order_frame.get_by_role("button", name="编 辑").click()
        expect(prod_order_frame.locator("body")).to_contain_text("生产订单已拆分，不能编辑！")

        logger.info("测试用例productionorder_split_cant_edit执行完成")