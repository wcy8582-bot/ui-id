import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestCustomerFormCheck(BaseTest):
    """
    用例名：table_properties
    用例ms的id：101250、101230
    """

    def test_customer_create_form_check(self, page: Page, project_name: str):
        f"""测试新增客户表单字段展示
        用例名：table_properties
        用例ms的id：101250、101230
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：table_properties")
        logger.info(f"用例ms的id：101250")
        logger.info("=" * 60)
        
        # 使用公用登录方法登录系统
        logger.info("调用公用登录方法完成登录")
        self.login(page, project_name)
        
        # 导航进入客户档案页面
        logger.info("导航进入客户档案模块")
        page.get_by_text("基础资料").click()
        page.get_by_text("客户档案").click()
        
        # 获取tab内容iframe，简化后续代码
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 点击新增客户按钮打开创建弹窗
        logger.info("点击新增按钮，打开创建客户弹窗")
        frame.get_by_role("button", name="plus-circle 新增").click()
        
        # 断言表单所有必填字段正常可见
        logger.info("开始断言表单所有字段展示正确")
        create_form = frame.get_by_label("创建客户").locator("form")
        expect(create_form).to_contain_text("客户编码")
        expect(frame.locator("div").filter(has_text=re.compile(r"^客户名称$")).nth(4)).to_be_visible()
        expect(frame.locator("div").filter(has_text=re.compile(r"^统一社会信用代码$")).first).to_be_visible()
        expect(frame.locator("div").filter(has_text=re.compile(r"^客户分类请选择客商分类$")).first).to_be_visible()
        expect(frame.locator("div").filter(has_text=re.compile(r"^业务员请选择人员$")).first).to_be_visible()
        expect(frame.locator("div").filter(has_text=re.compile(r"^价格等级$")).first).to_be_visible()
        expect(frame.locator("div").filter(has_text=re.compile(r"^期初应收款$")).first).to_be_visible()
        expect(frame.locator("div").filter(has_text=re.compile(r"^信用额度（元）$")).first).to_be_visible()
        expect(frame.locator("div").filter(has_text=re.compile(r"^联系人$")).first).to_be_visible()
        expect(frame.locator("div").filter(has_text=re.compile(r"^联系电话$")).first).to_be_visible()
        expect(frame.locator("div").filter(has_text=re.compile(r"^手机号码$")).first).to_be_visible()
        expect(frame.locator("div").filter(has_text=re.compile(r"^联系邮箱$")).first).to_be_visible()
        expect(frame.locator("div").filter(has_text=re.compile(r"^国家中国$")).first).to_be_visible()
        expect(frame.locator("div").filter(has_text=re.compile(r"^省份请选择省份$")).first).to_be_visible()
        expect(frame.locator("div").filter(has_text=re.compile(r"^市级请选择市级$")).first).to_be_visible()
        expect(frame.locator("div").filter(has_text=re.compile(r"^地区请选择地区$")).first).to_be_visible()
        expect(frame.locator("div").filter(has_text=re.compile(r"^地址$")).first).to_be_visible()
        expect(frame.get_by_text("备注0 /")).to_be_visible()
        
        # 关闭创建弹窗
        logger.info("所有字段断言完成，关闭创建客户弹窗")
        frame.get_by_role("button", name="Close").click()
        
        logger.info(f"用例table_properties执行完成")