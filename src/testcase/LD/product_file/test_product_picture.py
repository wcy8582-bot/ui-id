import re
import os
import pytest
from playwright.sync_api import Page, expect
from src.base.base_test import BaseTest
from src.common.logger import logger

class TestProductPicture(BaseTest):
    """
    用例名：product_picture
    用例ms的id：101210
    """

    def test_product_picture(self, page: Page, project_name: str):
        f"""测试产品图片上传预览删除功能
        用例名：product_picture
        用例ms的id：101210
        项目名：{project_name}

        Args:
            page: 页面实例
            project_name: 项目名称
        """
        logger.info("=" * 60)
        logger.info(f"开始执行用例：product_picture")
        logger.info(f"用例ms的id：101210")
        logger.info("=" * 60)
        
        # 调用公用登录方法
        logger.info("登录系统")
        self.login(page, project_name)
        
        # 进入产品档案模块
        logger.info("进入产品档案页面")
        page.get_by_text("基础资料").click()
        page.get_by_text("产品档案").click()
        
        # 获取iframe上下文
        product_frame = page.locator("iframe[name=\"supos-tab-framework-2\"]").content_frame
        
        # 点击新增产品
        logger.info("点击新增产品按钮")
        product_frame.get_by_role("button", name="plus-circle 新增").click()
        
        # 打开产品图片上传区域
        logger.info("进入产品图片上传环节")
        product_frame.get_by_label("创建产品").get_by_text("产品图片").click()
        
        # 获取测试图片的绝对路径
        test_image_path = r"D:\install\auto_ui-master\src\pages\LD\product_file\1.png"
        
        # 检查文件是否存在
        if not os.path.exists(test_image_path):
            raise FileNotFoundError(f"测试图片文件不存在: {test_image_path}")
        
        # 上传测试图片
        logger.info(f"上传测试图片文件: {test_image_path}")
        # 不要点击按钮，直接设置文件到隐藏的 input 元素
        product_frame.locator("input[type='file']").first.set_input_files(test_image_path)
        
        # 等待上传完成
        logger.info("等待图片上传处理完成")
        page.wait_for_timeout(2000)
        
        # 预览图片
        logger.info("点击预览图片")
        # 使用 data-icon 定位眼睛图标
        product_frame.locator("[data-icon='eye']").first.click()

        # 关闭弹窗
        logger.info("关闭预览弹窗")
        # 等待并点击预览弹窗右上角关闭按钮（使用 .last 解决严格模式冲突，指向最新出现的弹窗）
        product_frame.locator(".ant-modal-close").last.wait_for(state="visible", timeout=5000)
        product_frame.locator(".ant-modal-close").last.click()

        # 删除图片
        logger.info("删除上传的图片")
        # 使用 data-icon 定位删除图标
        product_frame.locator("[data-icon='delete']").click()
        
        logger.info("用例product_picture执行完成")