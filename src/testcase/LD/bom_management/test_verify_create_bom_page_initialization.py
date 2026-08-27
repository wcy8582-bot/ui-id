import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyCreateBomPageInitialization(BaseTest):
    """
    用例名：verify_create_bom_page_initialization
    用例ms的id：101228
    """

    def test_verify_create_bom_page_initialization(self, page: Page, project_name: str):
        f"""验证创建物料清单页面初始化渲染正确性
        用例名：verify_create_bom_page_initialization
        用例ms的id：101228
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_create_bom_page_initialization")
        logger.info(f"用例ms的ID：101228")
        logger.info("=" * 60)
        
        # 使用公用登录方法登录系统
        self.login(page, project_name)
        logger.info("系统登录成功")

        # 导航到物料清单页面
        logger.info("点击【基础资料】菜单")
        page.get_by_text("基础资料").click()
        logger.info("点击【物料清单】菜单")
        page.get_by_text("物料清单").click()

        # 提取iframe内容帧，避免重复定位
        bom_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 校验新增按钮可见性
        logger.info("校验物料清单页面新增按钮可见性")
        expect(bom_frame.get_by_role("button", name="plus-circle 新增")).to_be_visible()

        # 打开创建BOM弹窗
        logger.info("点击新增按钮，打开创建物料清单弹窗")
        bom_frame.get_by_role("button", name="plus-circle 新增").click()

        # 校验弹窗所有初始化元素渲染正确性
        logger.info("开始校验创建物料清单弹窗初始化元素")
        expect(bom_frame.get_by_text("父项产品信息")).to_be_visible()
        expect(bom_frame.get_by_role("dialog", name="创建物料清单").locator("form")).to_be_visible()
        expect(bom_frame.locator("div").filter(has_text=re.compile(r"^子项产品信息$"))).to_be_visible()
        expect(bom_frame.get_by_text("添加子项产品序号物料编号物料名称物料规格单位用量关联工序单位物料来源库存数量备注操作 暂无数据 To pick up a draggable item,")).to_be_visible()
        expect(bom_frame.get_by_label("创建物料清单").locator("form")).to_contain_text("父项产品")
        expect(bom_frame.get_by_label("创建物料清单").locator("form")).to_contain_text("产品规格")
        expect(bom_frame.get_by_label("创建物料清单").locator("form")).to_contain_text("物料来源")
        expect(bom_frame.get_by_label("创建物料清单").locator("form")).to_contain_text("工艺路线")
        expect(bom_frame.get_by_label("创建物料清单").locator("form")).to_contain_text("单位")
        expect(bom_frame.get_by_label("创建物料清单").locator("thead")).to_contain_text("序号")
        expect(bom_frame.get_by_label("创建物料清单").locator("thead")).to_contain_text("物料编号")
        expect(bom_frame.get_by_label("创建物料清单").locator("thead")).to_contain_text("物料名称")
        expect(bom_frame.get_by_label("创建物料清单").locator("thead")).to_contain_text("物料规格")
        expect(bom_frame.get_by_label("创建物料清单").locator("thead")).to_contain_text("单位用量")
        expect(bom_frame.get_by_label("创建物料清单").locator("thead")).to_contain_text("关联工序")
        expect(bom_frame.get_by_label("创建物料清单").locator("thead")).to_contain_text("单位")
        expect(bom_frame.get_by_label("创建物料清单").locator("thead")).to_contain_text("物料来源")
        expect(bom_frame.get_by_label("创建物料清单").locator("thead")).to_contain_text("库存数量")
        expect(bom_frame.get_by_label("创建物料清单").locator("thead")).to_contain_text("备注")
        expect(bom_frame.get_by_label("创建物料清单").locator("thead")).to_contain_text("操作")

        # 验证弹窗按钮可正常交互
        logger.info("验证弹窗按钮可正常点击")
        bom_frame.get_by_role("button", name="保 存").click()
        bom_frame.get_by_role("button", name="取 消").click()

        logger.info(f"用例verify_create_bom_page_initialization执行完成")