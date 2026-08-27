# -*- coding: utf-8 -*-
"""
失败瞬间现场采集钩子（failure_capture.py）

解决的问题：用例失败后浏览器随即关闭，DOM 不复存在，
事后（run.py/平台/AI 修复）想拿 HTML 无处可拿。
本模块在 pytest 的报告钩子中，于"失败已发生、浏览器未关闭"的
窗口期自动采集现场三件套（出错行 + 层级树/锚点 HTML + 截图），
序列化到磁盘，供失败后的 AI 修复循环使用。

接入方式（根目录 conftest.py 追加三行）：
    from src.common.failure_capture import capture_on_failure
    # 在已有的 pytest_runtest_makereport 钩子里调用：
    # capture_on_failure(item, report)
"""
import json
import os
import time
import traceback

from src.common.dom_snapshot import capture_snapshot
from src.common.logger import logger

SNAPSHOT_DIR = os.path.join("reports", "failure_snapshots")

# base_test 的 page fixture 创建页面时注册到这里，钩子里才能拿到 page
_current_page = None


def register_page(page):
    """base_test 创建 page 后调用：register_page(page)"""
    global _current_page
    _current_page = page


def unregister_page():
    global _current_page
    _current_page = None


def capture_on_failure(item, report) -> str | None:
    """在 pytest_runtest_makereport 钩子中调用。
    失败且是定位类错误时采集现场，返回 snapshot 文件路径；否则返回 None。
    """
    if not report.failed or report.when != "call":
        return None
    if _current_page is None:
        logger.warning("失败时无存活 page，无法采集现场")
        return None

    error_text = str(report.longrepr)

    # 只对"定位类失败"采集（断言失败等业务失败不需要 DOM）
    if not _is_locator_failure(error_text):
        return None

    case_dir = os.path.join(SNAPSHOT_DIR, f"{item.name}_{int(time.time())}")
    os.makedirs(case_dir, exist_ok=True)

    try:
        snapshot = capture_snapshot(
            _current_page,
            error_message=error_text,
            traceback_text=error_text,
            save_dir=case_dir,
        )
        snapshot["case_name"] = item.name
        snapshot["nodeid"] = item.nodeid

        path = os.path.join(case_dir, "snapshot.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"失败现场已采集: {path}")
        return path
    except Exception as e:
        # 采集失败绝不影响测试报告本身
        logger.warning(f"失败现场采集异常: {e}")
        return None


def _is_locator_failure(error_text: str) -> bool:
    markers = ("Timeout", "waiting for", "locator.", "selector",
               "not visible", "strict mode violation")
    return any(m in error_text for m in markers)
