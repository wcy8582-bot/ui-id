import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestWorkOrderDeleteInstance(BaseTest):
    """
    用例名：workorder_delete_instance
    用例ms的id：100465
    """

    def test_workorder_delete_instance(self, page: Page, project_name: str):
        f"""测试删除工单实例功能
        用例名：workorder_delete_instance
        用例ms的id：100465
        项目名：{project_name}  
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行workorder_delete_instance")
        logger.info(f"用例ms的id：100465")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 切换到WorkOrder iframe
        logger.info("切换到WorkOrder iframe")
        frame = page.locator("iframe[name=\"WorkOrder\"]").content_frame
        
        # 筛选已下发未结束执行中工单
        logger.info("筛选已下发未结束执行中工单")
        frame.get_by_role("button", name="已下发未结束").click()
        frame.get_by_role("combobox", name="执行状态 :").click()
        frame.get_by_text("执行中").nth(2).click()
        
        # 点击查询按钮
        logger.info("点击查询按钮")
        frame.get_by_role("button", name="查询").click()
        
        # 双击生效工单打开详情弹窗并关闭
        logger.info("双击生效工单打开详情弹窗并关闭")
        with page.expect_popup() as page1_info:
            frame.get_by_text("生效").nth(1).dblclick()
        page1 = page1_info.value
        page1.wait_for_load_state("networkidle")
        workorder_no = page1.locator("input#productBatch").input_value()
        logger.info(f"获取到工单号: {workorder_no}")
        page1.get_by_role("button", name="关 闭").click()
        page1.close()
        
        # 输入工单号并查询
        logger.info("输入工单号并查询")
        frame.get_by_role("textbox", name="工单号 :").fill(workorder_no)
        frame.get_by_role("button", name="查询").click()
        
        # 勾选实例并点击删除实例
        logger.info("勾选实例并点击删除实例")
        frame.get_by_label("", exact=True).check()
        frame.get_by_role("button", name="删除实例").click()
        
        # 点击确定删除
        logger.info("点击确定删除")
        frame.get_by_role("button", name="确 定").click()
        
        # 重置查询条件
        logger.info("重置查询条件")
        frame.get_by_role("button", name="重置").click()
        
        # 再次输入工单号并查询
        logger.info("再次输入工单号并查询")
        frame.get_by_role("textbox", name="工单号 :").fill(workorder_no)
        frame.get_by_role("button", name="查询").click()
        
        # 验证工单状态为待下发
        logger.info("验证工单状态为待下发")
        expect(frame.locator("tbody")).to_contain_text("待下发")