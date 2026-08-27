import re
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestVerifyMultiruleEnable(BaseTest):
    """
    用例名：verify_multirule_enable
    用例ms的id：101103
    """

    def test_verify_multirule_enable(self, page: Page, project_name: str):
        f"""测试验证多规则启用逻辑
        用例名：verify_multirule_enable
        用例ms的id：101103
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：verify_multirule_enable")
        logger.info(f"用例ms的id：101103")
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

        # 步骤1：翻页查找第一个状态为"启用"的规则
        logger.info("查找第一个状态为'启用'的规则")
        enabled_row = None
        business_type = None
        max_pages = 10

        for page_index in range(max_pages):
            logger.info(f"正在第 {page_index + 1} 页查找启用规则")

            # 尝试在当前页查找
            potential_row = content_frame.locator("tr").filter(
                has=content_frame.locator("td").nth(4).get_by_text("启用")
            ).first

            if potential_row.is_visible(timeout=2000):
                enabled_row = potential_row
                # 获取业务类型
                business_type_cell = enabled_row.locator("td").nth(3)
                business_type = business_type_cell.text_content()
                logger.info(f"在第 {page_index + 1} 页找到启用规则，业务类型：{business_type}")
                break

            # 如果没找到且不是最后一页，尝试点击下一页
            next_btn = content_frame.locator(".ant-pagination-next")
            if next_btn.is_visible() and "ant-pagination-disabled" not in (next_btn.get_attribute("class") or ""):
                next_btn.click()
                page.wait_for_timeout(1000)
            else:
                break

        if enabled_row is None or business_type is None:
            raise AssertionError("未找到状态为'启用'的规则")

        # 步骤2：翻页查找相同业务类型但状态为"停用"的规则
        logger.info(f"查找业务类型为'{business_type}'且状态为'停用'的规则")

        # 为了确保查找完整，先回到第一页
        logger.info("回到列表第一页开始查找停用规则")
        first_page_btn = content_frame.locator(".ant-pagination-item", has_text="1").first
        if first_page_btn.is_visible():
            first_page_btn.click()
            page.wait_for_timeout(1000)

        target_row = None
        for page_index in range(max_pages):
            all_rows = content_frame.locator("tbody tr")
            count = all_rows.count()

            found_in_page = False
            for i in range(count):
                row = all_rows.nth(i)
                if not row.is_visible():
                    continue

                try:
                    row_business_type = row.locator("td").nth(3).text_content()
                    row_status = row.locator("td").nth(4).text_content()

                    # 匹配业务类型且状态包含“停用”
                    if row_business_type.strip() == business_type.strip() and "停用" in row_status:
                        target_row = row
                        found_in_page = True
                        logger.info(f"在第 {page_index + 1} 页找到目标停用规则")
                        break
                except Exception as e:
                    logger.warning(f"处理第{i}行时出错：{e}")
                    continue

            if found_in_page:
                break

            # 翻页
            next_btn = content_frame.locator(".ant-pagination-next")
            if next_btn.is_visible() and "ant-pagination-disabled" not in (next_btn.get_attribute("class") or ""):
                next_btn.click()
                page.wait_for_timeout(1000)
            else:
                break

        # 验证找到目标行
        if target_row is None:
            logger.error(f"未找到业务类型为'{business_type}'且状态为'停用'的规则")
            raise AssertionError(f"未找到业务类型为'{business_type}'且状态为'停用'的规则")

        expect(target_row).to_be_visible()
        logger.info("成功定位到目标停用规则")

        # 步骤3：点击该行操作列的"启用"按钮
        logger.info("点击目标行的'启用'按钮")
        target_row.get_by_text("启用").first.click()

        # 步骤4：验证弹窗提示并取消
        logger.info("验证弹窗提示信息")
        expect(content_frame.get_by_text("当前业务类型已存在启用的编码规则")).to_be_visible()

        # 点击取消按钮
        logger.info("点击取消按钮")
        content_frame.get_by_role("button", name="取 消").click()

        logger.info("用例执行完成")
