import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyProdLineNameRejected(BaseTest):
    """
    用例名：verify_name_rejected
    用例ms的id：100977
    """

    def test_verify_prod_line_name_rejected(self, page: Page, project_name: str):
        f"""测试创建产线名称重复校验功能
        用例名：verify_name_rejected
        用例ms的id：100977
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_name_rejected")
        logger.info(f"用例ms ID：0")
        logger.info("=" * 60)
        
        # 使用公用登录方法登录系统
        logger.info("执行公用登录")
        self.login(page, project_name)
        
        # 导航到产线设置页面
        logger.info("导航到产线设置页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("基础信息").click()
        page.get_by_text("产线设置").click()
        
        # 获取主内容iframe
        main_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        # 打开新增产线弹窗
        logger.info("打开新增产线弹窗")
        main_frame.get_by_role("button", name="plus-circle 新增").click()
        create_dialog = main_frame.get_by_role("dialog", name="创建产线")
        
        # 填充产线基本信息（去除多余的前置点击操作，fill自动聚焦）
        logger.info("填充产线基本信息")
        create_dialog.locator("#prodLineCode").fill("11")
        create_dialog.locator("#prodLineName").fill("11")
        
        # 选择关联设备
        logger.info("选择关联设备")
        main_frame.locator(".ant-col.ant-col-24 > .ant-form-item-control-input > .ant-form-item-control-input-content > .refer-list > .anticon > svg").first.click()
        equip_frame = main_frame.locator("iframe[name=\"equipment\"]").content_frame
        equip_frame.get_by_role("cell", name="1", exact=True).click()
        equip_frame.get_by_role("row").nth(1).get_by_role("checkbox").check()
        main_frame.get_by_role("dialog", name="选择设备").get_by_role("button", name="保 存").click()

        # 选择关联部门
        logger.info("选择关联部门")
        main_frame.locator(".ant-col.ant-col-24 > .ant-form-item-control-input > .ant-form-item-control-input-content > .refer-list > .anticon > svg").click()
        depart_frame = main_frame.locator("iframe[name=\"depart\"]").content_frame
        depart_frame.get_by_text("生产部门").click()
        main_frame.get_by_role("dialog", name="选择部门").get_by_role("button", name="保 存").click()


        
        # 提交表单，验证重复提示
        logger.info("提交表单，验证产线名称重复校验逻辑")
        main_frame.get_by_role("button", name="保 存").click()
        # 添加断言验证预期结果
        expect(main_frame.locator("div").filter(has_text="产线名称重复！").nth(3)).to_be_visible()
        logger.info("成功捕获'产线名称重复！'提示，校验通过")
        
        # 关闭新增弹窗
        logger.info("关闭新增产线弹窗")
        main_frame.get_by_role("button", name="取 消").click()
        
        logger.info(f"用例verify_name_rejected执行完成")