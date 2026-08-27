import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger
from src.common.tool import Tool
from src.common.data_generator import DataGenerator



class TestProductionOrderSufficientSplitQuantity(BaseTest):
    """
    用例名：productionorder_sufficient_split_quantity
    用例ms的id：100106
    """

    def test_productionorder_sufficient_split_quantity(self, page: Page, project_name: str):
        f"""测试生产订单足额拆分功能
        用例名：productionorder_sufficient_split_quantity
        用例ms的id：100106
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：productionorder_sufficient_split_quantity")
        logger.info(f"用例ms ID：100106")
        logger.info("=" * 60)
        
        # 使用公用登录方法登录系统
        logger.info("调用公用登录方法完成登录")
        self.login(page, project_name)
        
        # 进入生产订单模块
        logger.info("进入生产计划->生产订单页面")
        page.get_by_role("listitem", name="生产计划").click()
        page.get_by_text("生产订单").click()

        # 创建生产订单
        logger.info("开始创建生产订单")
        order_no = Tool.create_production_order(page, "100", "测试订单")
        if order_no:
            logger.info(f"生产订单创建成功: {order_no}")
        else:
            logger.error("创建生产订单失败")
            # 用例直接失败，不继续后续步骤
            pytest.fail("创建生产订单失败")
        
        # 获取生产订单iframe，简化后续定位
        po_iframe = page.locator("iframe[name=\"ProductionOrders\"]").content_frame
        logger.info("获取生产订单页面iframe实例成功")

        # 查询目标测试订单
        logger.info(f"查询目标订单：{order_no}")
        po_iframe.get_by_role("textbox", name="订单号 :").click()
        po_iframe.get_by_role("textbox", name="订单号 :").fill(order_no)
        po_iframe.get_by_role("button", name="查询").click()

        # 第一次拆分订单
        logger.info("开始执行第一次拆分")
        po_iframe.get_by_label("", exact=True).check()
        po_iframe.get_by_role("button", name="拆分").click()
        po_iframe.get_by_role("button", name="增 行").click()
        po_iframe.locator(".ant-table-cell > .ant-input").first.click()
        po_iframe.locator(".ant-table-cell > .ant-input").first.fill(DataGenerator().get_order_no("SCDD"))
        po_iframe.get_by_role("spinbutton").nth(2).click()
        po_iframe.get_by_role("spinbutton").nth(2).fill("50")
        po_iframe.get_by_role("button", name="确 定").click()
        logger.info("第一次拆分提交完成")

        # 第二次拆分订单
        logger.info("开始执行第二次拆分")
        po_iframe.get_by_role("button", name="查询").click()
        po_iframe.get_by_role("button", name="拆分").click()
        
        # 验证可拆分数量
        logger.info("验证可拆分数量")
        remain_split_num_input = po_iframe.locator("#remainSplitNum")
        remain_split_num = remain_split_num_input.get_attribute("aria-valuenow")
        logger.info(f"当前可拆分数量: {remain_split_num}")
        
        # 总数量是100，第一次拆分了50，所以可拆分数量应该是50
        expected_remain = 50
        assert remain_split_num == str(expected_remain), f"可拆分数量不正确，期望: {expected_remain}，实际: {remain_split_num}"
        logger.info("验证通过：可拆分数量正确")
        po_iframe.get_by_role("button", name="增 行").click()
        po_iframe.locator(".ant-table-cell > .ant-input").first.click()
        po_iframe.locator(".ant-table-cell > .ant-input").first.fill(DataGenerator().get_order_no("SCDD"))
        po_iframe.get_by_role("spinbutton").nth(2).click()
        po_iframe.get_by_role("spinbutton").nth(2).fill("10")
        po_iframe.get_by_role("button", name="确 定").click()
        logger.info("第二次拆分提交完成")

        # 验证拆分结果
        logger.info("验证拆分执行结果")
        expect(po_iframe.locator("body")).to_contain_text("拆分成功")
        
        # 再次验证可拆分数量（如果需要）
        logger.info("再次验证可拆分数量")
        po_iframe.get_by_role("button", name="查询").click()
        po_iframe.get_by_role("button", name="拆分").click()
        
        remain_split_num_input = po_iframe.locator("#remainSplitNum")
        remain_split_num = remain_split_num_input.get_attribute("aria-valuenow")
        logger.info(f"当前可拆分数量: {remain_split_num}")
        
        # 总数量是100，第一次拆分了50，第二次拆分了10，所以可拆分数量应该是40
        expected_remain = 40
        assert remain_split_num == str(expected_remain), f"可拆分数量不正确，期望: {expected_remain}，实际: {remain_split_num}"
        logger.info("验证通过：可拆分数量正确")
        
        # 关闭拆分弹窗
        po_iframe.get_by_role("button", name="取 消").click()
        
        logger.info("用例执行完成，结果符合预期")