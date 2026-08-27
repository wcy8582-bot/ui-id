import re
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestVerifyEnableSureAction(BaseTest):
    """
    用例名：verify_enable_sure_action
    用例ms的id：101077
    """

    def test_verify_enable_sure_action(self, page: Page, project_name: str):
        f"""测试编码规则编辑-确定功能
        用例名：verify_enable_sure_action
        用例ms的id：101077
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_enable_sure_action")
        logger.info(f"用例ms的id：101077")
        logger.info("=" * 60)

        # 使用公用登录方法
        self.login(page, project_name)

        # 进入编码规则配置页面
        logger.info("进入编码规则配置菜单")
        page.get_by_text("基础资料").click()
        page.get_by_text("编码规则配置").click()

        # 获取目标iframe，优化重复定位代码
        content_iframe = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame

        # 选择目标编码规则记录，点击编辑按钮
        logger.info("选择目标编码规则，进入编辑")
        
        # 等待列表加载
        logger.info("等待规则列表加载")
        page.wait_for_timeout(1000)
        
        # 翻页查找第一个状态为"停用"的规则
        logger.info("查找第一个状态为'停用'的规则")
        target_row = None
        max_pages = 10
        
        for page_index in range(max_pages):
            logger.info(f"正在第 {page_index + 1} 页查找停用规则")
            
            # 尝试在当前页查找
            potential_row = content_iframe.locator("tr").filter(
                has=content_iframe.locator("td").nth(4).get_by_text("停用")
            ).first
            
            if potential_row.is_visible(timeout=2000):
                target_row = potential_row
                logger.info(f"在第 {page_index + 1} 页找到停用规则")
                break
            
            # 如果没找到且不是最后一页，尝试点击下一页
            next_btn = content_iframe.locator(".ant-pagination-next")
            if next_btn.is_visible() and "ant-pagination-disabled" not in (next_btn.get_attribute("class") or ""):
                next_btn.click()
                page.wait_for_timeout(1000)
            else:
                break
        
        # 验证找到目标行
        if target_row is None:
            raise AssertionError("未找到状态为'停用'的规则")
        
        # 验证找到目标行并点击编辑
        expect(target_row).to_be_visible()
        target_row.get_by_text("编辑").first.click()

        # 点击确定提交编辑
        logger.info("点击保存按钮提交编辑操作")
        content_iframe.get_by_role("button", name="保 存").click()

        logger.info("verify_enable_sure_action用例执行完成")