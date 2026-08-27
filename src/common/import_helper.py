"""通用导入动作封装

把"上传 Excel → 等待导入成功提示"这一稳定动作抽出来，
供所有"导入类"用例复用，避免每个用例重复编写上传与断言代码。

典型用法：
    from src.common.import_helper import ImportHelper

    main_frame = page.locator("iframe[name='supos-tab-framework-1']").content_frame
    importer = ImportHelper(main_frame)
    importer.upload_and_verify(excel_path)
"""
import os
from typing import Union

from playwright.sync_api import Page, Frame, Locator, expect

from src.common.logger import logger


class ImportHelper:
    """通用 Excel 导入助手

    通过直接给隐藏的 input[type='file'] 赋值实现上传，
    省去点击"导入"按钮和等待系统文件选择对话框的过程，更稳定。
    """

    # 默认的导入成功提示文案
    DEFAULT_SUCCESS_TEXT = "导入文件成功！"

    def __init__(self, frame: Union[Page, Frame, Locator], file_input_selector: str = "input[type='file']"):
        """初始化导入助手

        Args:
            frame: 操作作用域，可以是 Page、Frame 或 Locator（如弹窗容器）
            file_input_selector: 文件上传 input 的选择器，默认为 input[type='file']
        """
        self.frame = frame
        self.file_input_selector = file_input_selector

    def upload(self, excel_path: str) -> None:
        """上传 Excel 文件（不做断言）

        Args:
            excel_path: Excel 文件绝对路径
        """
        if not os.path.exists(excel_path):
            raise FileNotFoundError(f"待导入的 Excel 文件不存在: {excel_path}")

        logger.info(f"开始上传 Excel 文件: {excel_path}")
        self.frame.locator(self.file_input_selector).set_input_files(excel_path)
        logger.info("Excel 文件已提交到页面")

    def verify_success(self, success_text: str = DEFAULT_SUCCESS_TEXT, timeout: int = 30000) -> None:
        """验证导入成功提示出现

        Args:
            success_text: 期望出现的成功提示文案
            timeout: 最长等待时间（毫秒）
        """
        logger.info(f"等待导入成功提示出现: '{success_text}'")
        expect(self.frame.get_by_role("alert")).to_contain_text(success_text, timeout=timeout)
        logger.info("导入成功提示已出现")

    def upload_and_verify(
        self,
        excel_path: str,
        success_text: str = DEFAULT_SUCCESS_TEXT,
        timeout: int = 30000,
    ) -> None:
        """上传并验证导入成功（最常用入口）

        Args:
            excel_path: Excel 文件绝对路径
            success_text: 期望出现的成功提示文案
            timeout: 最长等待时间（毫秒）
        """
        self.upload(excel_path)
        self.verify_success(success_text=success_text, timeout=timeout)

    def verify_error(self, error_text: str, timeout: int = 30000) -> None:
        """验证导入失败提示出现（用于负面用例）

        Args:
            error_text: 期望出现的错误提示文案（支持部分匹配）
            timeout: 最长等待时间（毫秒）
        """
        logger.info(f"等待导入失败提示出现: '{error_text}'")
        expect(self.frame.get_by_role("alert")).to_contain_text(error_text, timeout=timeout)
        logger.info("导入失败提示已出现")

    def verify_partial_success(
        self,
        success_count: int,
        fail_count: int = 0,
        timeout: int = 30000,
    ) -> None:
        """验证部分导入成功提示（含成功/失败条数）

        适用于"批量导入部分成功"场景，系统通常会弹出
        "成功 X 条，失败 Y 条"的提示。

        Args:
            success_count: 期望的成功条数
            fail_count: 期望的失败条数，0 表示不校验失败数
            timeout: 最长等待时间（毫秒）
        """
        logger.info(f"等待部分成功提示: 成功 {success_count} 条, 失败 {fail_count} 条")
        alert = self.frame.get_by_role("alert")
        expect(alert).to_contain_text(f"成功{success_count}", timeout=timeout)
        if fail_count > 0:
            expect(alert).to_contain_text(f"失败{fail_count}", timeout=timeout)
        logger.info("部分成功提示已出现")

    def upload_and_verify_error(
        self,
        excel_path: str,
        error_text: str,
        timeout: int = 30000,
    ) -> None:
        """上传并验证导入失败（负面用例入口）

        Args:
            excel_path: Excel 文件绝对路径
            error_text: 期望出现的错误提示文案
            timeout: 最长等待时间（毫秒）
        """
        self.upload(excel_path)
        self.verify_error(error_text=error_text, timeout=timeout)

    def download_template(self, button_name: str = "下载模板", save_dir: str = "test_data") -> str:
        """点击下载模板按钮并等待文件下载完成

        Args:
            button_name: 下载模板按钮的文案
            save_dir: 模板保存目录

        Returns:
            下载后的模板文件绝对路径
        """
        import os
        os.makedirs(save_dir, exist_ok=True)

        logger.info(f"点击 '{button_name}' 按钮，等待下载模板")
        with self.frame.expect_download() as download_info:
            self.frame.get_by_role("button", name=button_name).click()
        download = download_info.value
        save_path = os.path.join(save_dir, download.suggested_filename)
        download.save_as(save_path)
        logger.info(f"模板已下载到: {save_path}")
        return save_path
