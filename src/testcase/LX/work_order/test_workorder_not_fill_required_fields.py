import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestAddWorkOrder(BaseTest):
    """
    用例名：workorder_not_fill_required_fields
    用例ms的id：100404
    """

    def test_add_work_order_missing_required_fields(self, page: Page, project_name: str):
        f"""测试新增生产工单必填项校验功能
        用例名：workorder_not_fill_required_fields
        用例ms的id：100404
        项目名：{project_name}
        
        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info("开始执行新增生产工单必填项校验测试")
        logger.info(f"用例ms的id：100404")
        logger.info("=" * 60)
        
        # 使用公用登录方法
        self.login(page, project_name)
        
        # 进入生产工单页面
        logger.info("进入生产工单页面")
        page.get_by_role("listitem", name="生产管理").click()
        page.get_by_text("生产工单").click()
        
        # 点击新增按钮，弹出新增窗口
        logger.info("点击新增按钮，弹出新增生产工单窗口")
        with page.expect_popup() as page1_info:
            page.locator("iframe[name=\"WorkOrder\"]").content_frame.get_by_role("button", name="新 增").click()
        page1 = page1_info.value
        
        # 不填写任何内容直接点击保存按钮
        logger.info("不填写任何内容直接点击保存按钮")
        page1.get_by_role("button", name="保 存").click()
        
        # 断言工单号必填提示信息
        logger.info("验证工单号必填提示信息")
        workorder_required_tip = page1.locator("span").filter(has_text="请输入工单号")
        expect(workorder_required_tip).to_be_visible()
        logger.info("工单号必填提示信息验证通过")
        
        # 关闭新增窗口
        logger.info("关闭新增生产工单窗口")
        page1.close()
        
        # 关闭主页面
        logger.info("关闭主页面")
        page.close()
        
        logger.info("=" * 60)
        logger.info("新增生产工单必填项校验测试执行完成")
        logger.info("=" * 60)