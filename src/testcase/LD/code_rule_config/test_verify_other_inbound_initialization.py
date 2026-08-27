import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyOtherInboundInitialization(BaseTest):
    """
    用例名：verify_other_inbound_initialization
    用例ms的id：101090
    """

    def test_verify_other_inbound_initialization(self, page: Page, project_name: str):
        f"""测试编码规则配置查看返回功能
        用例名：verify_other_inbound_initialization
        用例ms的id：101090
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_other_inbound_initialization")
        logger.info(f"用例ms的id：101090")
        logger.info("=" * 60)

        # 使用公用登录方法
        self.login(page, project_name)

        # 进入编码规则配置页面
        logger.info("进入编码规则配置菜单")
        page.get_by_text("基础资料").click()
        page.get_by_text("编码规则配置").click()

        # 获取iframe上下文
        content_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame

        # 等待列表加载
        logger.info("等待规则列表加载")
        page.wait_for_timeout(1000)

        # 翻页查找目标数据
        target_row = None
        max_pages = 10  # 最大翻页数，防止死循环
        
        for page_index in range(max_pages):
            logger.info(f"正在第 {page_index + 1} 页查找业务类型为'其它入库批号'的规则")
            
            # 在当前页查找目标行
            target_row = content_frame.locator("tr").filter(
                has=content_frame.locator("td").nth(3).get_by_text("其它入库批号")
            ).first
            
            # 如果找到目标行，退出循环
            if target_row.is_visible(timeout=2000):
                logger.info(f"在第 {page_index + 1} 页找到目标数据")
                break
            
            # 如果没找到且不是最后一页，尝试点击下一页
            next_btn = content_frame.locator(".ant-pagination-next")
            if next_btn.is_visible() and not next_btn.get_attribute("class").__contains__("ant-pagination-disabled"):
                logger.info(f"当前页未找到，点击下一页")
                next_btn.click()
                page.wait_for_timeout(1000)  # 等待下一页数据加载
            else:
                logger.warning("已到达最后一页，停止翻页")
                break
        
        # 验证是否找到目标行
        if target_row is None or not target_row.is_visible():
            logger.error("未找到业务类型为'其它入库批号'的规则")
            raise AssertionError("未找到业务类型为'其它入库批号'的规则")

        # 验证找到目标行
        expect(target_row).to_be_visible()
        logger.info("成功定位到第一个业务类型为'其它入库批号'的规则")

        # 点击该行的"查看"按钮
        logger.info("点击目标行的'查看'按钮")
        target_row.get_by_text("查看").first.click()

        # 点击返回完成操作
        logger.info("完成查看，点击返回")
        content_frame.get_by_role("button", name="返 回").click()

        logger.info(f"用例verify_other_inbound_initialization执行完成")