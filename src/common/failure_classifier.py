# -*- coding: utf-8 -*-
"""
失败归因分类 + 修复路由模块（failure_classifier.py）

解决的问题：错误类型不同，需要的修复信息完全不同——
不加区分地把 DOM 全喂给 AI，会引入噪声、误导修复方向、浪费 token。
本模块先用确定性规则把失败分类，再按类别路由到不同的修复策略，
每类只给 AI 它需要的信息（精准喂料），并规定不同的修复权限。

一处分类，两个消费者：
  ① 修复路由：决定给什么信息、允不允许自动修
  ② 统计分析：失败归因占比（"定位失效占六成"的数据来源）
"""
from enum import Enum

from src.common.logger import logger


class FailureType(str, Enum):
    LOCATOR = "locator"        # 定位失效：元素找不到/不可见
    IFRAME = "iframe"          # iframe 相关：frame 定位失败/层级变化
    ASSERTION = "assertion"    # 断言失败：预期与实际不符
    TIMEOUT = "timeout"        # 页面/接口加载超时（非定位类）
    SESSION = "session"        # 登录态失效/会话过期
    DATA = "data"              # 测试数据问题（唯一性冲突/前置数据缺失）
    ENV = "env"                # 环境故障（连接拒绝/服务不可达）
    UNKNOWN = "unknown"


# 规则表：按优先级从上到下匹配，命中即归类
_RULES = [
    (FailureType.IFRAME, ["content_frame", "frame detached",
                          "Frame has been detached", "iframe"]),
    (FailureType.LOCATOR, ["waiting for locator", "waiting for selector",
                           "strict mode violation", "not visible",
                           "Locator.", "element is not attached"]),
    (FailureType.ASSERTION, ["AssertionError", "assert ", "expect(",
                             "to_have_text", "to_be_visible 报错 but"]),
    (FailureType.SESSION, ["401", "Unauthorized", "登录", "login",
                           "session", "token"]),
    (FailureType.DATA, ["Unique constraint", "Duplicate entry",
                        "已存在", "UNIQUE constraint failed"]),
    (FailureType.ENV, ["Connection refused", "net::ERR_",
                       "502", "503", "Name or service not known"]),
    (FailureType.TIMEOUT, ["Timeout", "TimeoutError", "timed out"]),
    # TIMEOUT 放最后：定位类错误也含 Timeout 字样，先被 LOCATOR 拦截
]


def classify(error_text: str) -> tuple[FailureType, str]:
    """规则分类。返回 (类别, 命中理由)。规则全不中 → UNKNOWN（留给 AI 深度分析）。"""
    for ftype, markers in _RULES:
        for marker in markers:
            if marker in error_text:
                reason = f"命中特征: {marker}"
                logger.info(f"失败归类: {ftype.value}（{reason}）")
                return ftype, reason
    return FailureType.UNKNOWN, "规则未命中"


# ============================================================
# 修复路由表：每类失败 给什么信息、用什么策略、权限到哪
# ============================================================

REPAIR_STRATEGY = {
    FailureType.LOCATOR: {
        "context": ["error_line", "anchor_html", "ax_tree", "screenshot"],
        "auto_fix": True,           # 允许自动修复（验证通过才生效）
        "max_rounds": 2,
        "note": "定位类：给 DOM 现场三件套，AI 候选+唯一可见验证",
    },
    FailureType.IFRAME: {
        "context": ["error_line", "frame_list", "ax_tree", "screenshot"],
        "auto_fix": True,
        "max_rounds": 2,
        "note": "iframe 类：重点给 frame 探测结果，做 frame/主文档双向修复",
    },
    FailureType.ASSERTION: {
        "context": ["error_line", "expected_actual"],   # 只给预期vs实际
        "auto_fix": False,          # ★ 禁止自动修：断言失败=真bug或需求变更
        "max_rounds": 0,
        "note": "断言类：不喂 DOM（防止误导成改定位器），标记人工研判",
    },
    FailureType.SESSION: {
        "context": ["error_line"],
        "auto_fix": True,
        "max_rounds": 1,
        "note": "会话类：不喂 DOM，策略是重新登录后重试",
    },
    FailureType.DATA: {
        "context": ["error_line", "test_data"],
        "auto_fix": False,
        "max_rounds": 0,
        "note": "数据类：不修被测代码，检查造数/清理逻辑",
    },
    FailureType.ENV: {
        "context": ["error_line"],
        "auto_fix": False,
        "max_rounds": 0,
        "note": "环境类：不修代码，标记基础设施问题，环境恢复后重跑",
    },
    FailureType.TIMEOUT: {
        "context": ["error_line", "screenshot"],   # 截图看页面卡在哪
        "auto_fix": False,
        "max_rounds": 0,
        "note": "加载超时：非定位问题，DOM 意义不大，排查性能/网络",
    },
    FailureType.UNKNOWN: {
        "context": ["error_line", "ax_tree", "screenshot", "log_tail"],
        "auto_fix": False,
        "max_rounds": 0,
        "note": "未知类：信息给全但只诊断不自动修，人工确认后再放行",
    },
}


def route(error_text: str) -> dict:
    """分类 + 路由：返回该类失败的完整处置策略。"""
    ftype, reason = classify(error_text)
    strategy = REPAIR_STRATEGY[ftype]
    return {
        "type": ftype.value,
        "reason": reason,
        "context_fields": strategy["context"],   # 喂 AI 的信息白名单
        "auto_fix": strategy["auto_fix"],        # 修复权限
        "max_rounds": strategy["max_rounds"],
        "note": strategy["note"],
    }


def build_ai_context(route_info: dict, snapshot: dict) -> dict:
    """按白名单从 snapshot 里挑信息——不在白名单里的一律不给（防噪声）。"""
    return {k: snapshot.get(k) for k in route_info["context_fields"]
            if snapshot.get(k) is not None}
