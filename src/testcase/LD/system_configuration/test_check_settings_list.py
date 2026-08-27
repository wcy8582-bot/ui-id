import re
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger


class TestCheckSettingsList(BaseTest):
    """
    用例名：check_settings_list
    用例ms的id：101124
    """

    def test_check_settings_list(self, page: Page, project_name: str):
        f"""测试标签打印配置列表表头校验
        用例名：check_settings_list
        用例ms的id：101124
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：check_settings_list")
        logger.info(f"用例ms的id：10112")
        logger.info("=" * 60)

        # 使用公用登录方法登录系统
        logger.info("调用公用登录方法完成登录")
        self.login(page, project_name)

        # 进入标签打印配置菜单
        logger.info("进入标签打印配置页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("系统配置").click()
        page.get_by_text("标签打印配置").click()

        # 获取iframe内容框架，简化后续定位
        frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        logger.info("点击页面刷新按钮")
        frame.locator("img").click()

        # 校验表头所有字段存在
        logger.info("开始校验列表表头信息")
        thead_loc = frame.locator("thead")
        expect(thead_loc).to_contain_text("序号")
        expect(thead_loc).to_contain_text("模板ID")
        expect(thead_loc).to_contain_text("模板名称")
        expect(thead_loc).to_contain_text("模板类型")
        expect(thead_loc).to_contain_text("所属业务")
        expect(thead_loc).to_contain_text("创建人")
        expect(thead_loc).to_contain_text("创建时间")
        expect(thead_loc).to_contain_text("更新人")
        expect(thead_loc).to_contain_text("更新时间")
        expect(thead_loc).to_contain_text("操作")

        # 校验行操作按钮存在
        logger.info("校验列表行操作按钮信息")
        tbody_loc = frame.locator("tbody")
        expect(tbody_loc).to_contain_text("编辑")
        expect(tbody_loc).to_contain_text("删除")

        logger.info("用例check_settings_list执行完成")