import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool
from src.common.data_generator import DataGenerator


class TestProductionOrderSplitAddRow(BaseTest):
    """
    用例名：productionorder_split_add_row
    用例ms的id：100121
    """

    def test_productionorder_split_add_row(self, page: Page, project_name: str):
        f"""测试生产订单拆分增行功能
        用例名：productionorder_split_add_row
        用例ms的id：100121
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行测试用例：productionorder_split_add_row")
        logger.info(f"用例ms ID：100121")
        logger.info("=" * 60)
        
        # 调用封装好的公用登录方法
        logger.info("登录目标系统")
        self.login(page, project_name)
        
        # 导航到生产订单模块
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

        # 获取生产订单iframe，简化后续定位
        order_frame = page.locator("iframe[name=\"ProductionOrders\"]").content_frame
        logger.info("加载生产订单iframe完成")
        
        # 输入订单号查询目标订单
        logger.info("查询目标订单")
        order_frame.get_by_role("textbox", name="订单号 :").fill(order_no)
        order_frame.get_by_role("button", name="查询").click()
        
        # 选中订单发起拆分
        logger.info("选中订单并点击拆分按钮")
        order_frame.get_by_label("", exact=True).check()
        order_frame.get_by_role("button", name="拆分").click()

        # 获取拆分单据基础信息
        page_msg = Tool.get_split_order_info(page)
        logger.info(page_msg)
        if page_msg["order_no"] is None:
            logger.error("获取拆分单据基础信息失败")
            # 用例直接失败，不继续后续步骤
            pytest.fail("获取拆分单据基础信息失败")
        
        # 新增拆分行并录入拆分信息
        logger.info("点击增行，录入拆分信息")
        insert_date = DataGenerator().get_random_end_date(page_msg["plan_end_time"])
        batch_no = DataGenerator().get_order_no("SCPH")
        logger.info(f"生成的拆分批次号: {batch_no}")
        order_frame.get_by_role("button", name="增 行").click()
        order_frame.locator(".ant-table-cell > .ant-input").first.fill(batch_no)
        order_frame.get_by_role("spinbutton").nth(2).fill("1000")
        order_frame.locator("div:nth-child(6) > .ant-input").fill("测试订单")
        order_frame.get_by_role("textbox", name="请选择日期").first.fill(insert_date)
        
        # 确认日期操作
        logger.info("确认日期操作")
        order_frame.get_by_text("订单拆分").click()
        order_frame.get_by_label("确认").get_by_role("button", name="确 定").click()
        
        # 再次增行，校验数据自动带入功能
        logger.info("再次点击增行，校验自动带入数据正确性")
        order_frame.get_by_role("button", name="增 行").click()
        
        # 结果断言
        logger.info("执行结果断言")
        logger.info(f"校验日期: {insert_date}")
        expect(order_frame.get_by_role("textbox", name="请选择日期").nth(1)).to_have_value(insert_date)
        logger.info(f"校验批次号: {batch_no}")
        # 使用更精确的定位器找到批次号输入框
        batch_no_input = order_frame.locator(".ant-table-cell.ant-table-cell-ellipsis > .ant-input").first
        expect(batch_no_input).to_have_value(batch_no)
        logger.info(f"校验数量: 1000")
        expect(order_frame.get_by_role("spinbutton").nth(3)).to_have_value("1000")
        logger.info(f"校验备注: 测试订单")
        expect(order_frame.locator("div:nth-child(2) > div:nth-child(6) > .ant-input")).to_have_value("测试订单")
        
        
        logger.info(f"测试用例productionorder_split_add_row执行完成")