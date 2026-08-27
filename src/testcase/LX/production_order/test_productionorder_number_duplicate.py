import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestProductionOrderNumberDuplicate(BaseTest):
    """
    用例名：productionorder_number_duplicate
    用例ms的id：100083
    """

    def test_productionorder_number_duplicate(self, page: Page, project_name: str):
        f"""测试生产订单重复新增功能
        用例名：productionorder_number_duplicate
        用例ms的id：100083
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行productionorder_number_duplicate")
        logger.info(f"用例ms的id：100083")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产订单页面
        logger.info("进入生产订单页面")
        page.get_by_role("listitem", name="生产计划").click()
        page.get_by_text("生产订单").click()
        
        # 获取订单查看上下文
        frame = page.locator("iframe[name=\"ProductionOrders\"]").content_frame
        
        # 选中已有订单并查看关闭
        logger.info("选中已有订单并查看关闭")
        frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        frame.get_by_role("button", name="查 看").click()
        
        # 等待模态框加载完成
        logger.info("等待模态框加载完成")
        modal_content = frame.locator(".ant-modal-content")
        modal_content.wait_for(state="visible", timeout=20000)
        
        # 获取弹窗中的订单号
        logger.info("获取弹窗中的订单号")
        # 使用更精确的定位器，先找到模态框，再在模态框内找订单号输入框
        order_input = frame.locator(".ant-modal-content #orderNo")
        order_input.wait_for(state="visible", timeout=10000)
        order_number = order_input.get_attribute("value")
        logger.info(f"获取到的订单号: {order_number}")
        
        # 验证获取到了订单号
        assert order_number is not None, "未能获取到订单号"
        assert len(order_number) > 0, "获取到的订单号为空"
        
        frame.get_by_role("button", name="关 闭").click()
        
        # 点击新增按钮
        logger.info("点击新增按钮")
        frame.get_by_role("button", name="新 增").click()
        
        # 填写已存在的订单号
        logger.info("填写已存在的订单号")
        frame.get_by_role("textbox", name="请输入").fill(order_number)
        
        # 填写计划数量
        logger.info("填写计划数量")
        frame.get_by_role("spinbutton", name="* 计划数量").fill("100")
        
        # 选择物料
        logger.info("选择物料")
        refer_button = frame.locator("button.ant-btn-icon-only").nth(6)  
        refer_button.wait_for(state="visible", timeout=20000)
        refer_button.evaluate("el => el.click()")
        logger.info("成功: 物料参照按钮已点击")
        frame.locator("iframe").content_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        frame.get_by_label("物料参照").get_by_role("button", name="确 定").click()

            # 点击车间/产线参照按钮
        refer_button = frame.locator("button.ant-btn-icon-only").nth(5)  # 第二个按钮
        refer_button.wait_for(state="visible", timeout=20000)
        refer_button.evaluate("el => el.click()")
        logger.info("成功: 车间/产线参照按钮已点击")
        frame.locator("iframe").content_frame.get_by_role("row").nth(1).get_by_label("", exact=True).check()
        frame.get_by_label("车间/产线参照").get_by_role("button", name="确 定").click()
        
        # 点击确定提交表单
        logger.info("点击确定提交表单")
        frame.get_by_role("button", name="确 定").click()
        
        # 验证订单号已存在的提示
        logger.info("验证订单号已存在的提示")
        expect(frame.locator("body")).to_contain_text("订单号已存在！")