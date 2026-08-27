# -*- coding: utf-8 -*-
"""
定位自修复主流程（self_heal.py）

挂载点：base_page 的元素操作封装层（click/fill 等）。
触发条件：原定位器 20s（HEAL_THRESHOLD）未命中。

核心设计（攻克"精准提取定位点"的关键）：
  AI 不直接"写定位器"（容易幻觉、语法错、命中隐藏节点），
  AI 只负责"认出目标元素"，定位器由代码从真实 DOM 节点上提取特征生成：
    · 文本通道：AI 从 AX Tree 里选出目标节点 → 代码按 role+name 构造定位器
    · 视觉通道：AI（多模态）返回目标在截图中的坐标
                → 代码用 document.elementFromPoint(x,y) 映射回真实 DOM 节点
                → 代码从节点属性提取特征构造定位器
  两条通道的产物都必须过 count==1 && visible 确定性验证才允许重试。

信息输入（四重证据三角定位，提高命中率）：
  ① 元素意图描述 desc（page 对象里存的语义："审批弹窗的提交按钮"）
  ② 失效定位器本身（旧 id/旧文本仍是搜索线索）
  ③ 现场层级树 + 锚点子树（dom_snapshot 采集）
  ④ 页面截图（视觉通道）
"""
import json
import traceback

from playwright.sync_api import TimeoutError as PlaywrightTimeout

from src.common.dom_snapshot import capture_snapshot
from src.common.ai_chat import chat           # 框架已有的大模型调用封装
from src.common.logger import logger

HEAL_THRESHOLD_MS = 20000     # 20s 未命中触发自修复
RETRY_BUDGET_MS = 10000       # 修复后重试预算（总超时 30s 的剩余部分）


# ============================================================
# 挂载点：两段式等待 + 失败触发自愈
# ============================================================

def click_with_heal(page, locator: str, desc: str = "", timeout: int = 30000):
    """替代 page.click 的封装：先正常等待，超时进入自愈，自愈后重试。

    desc: 元素意图描述（page 对象里维护），是 AI 认出目标的最强线索。
    """
    try:
        page.click(locator, timeout=HEAL_THRESHOLD_MS)
        return
    except PlaywrightTimeout as e:
        logger.warning(f"定位 {HEAL_THRESHOLD_MS}ms 未命中，触发自修复: {locator}")

    new_locator = heal_locator(page, locator, desc, e)
    if not new_locator:
        raise                       # 修不了 → 按原逻辑失败，不掩盖真 bug

    # 用剩余预算重试；业务断言仍在后面守着，找错元素也过不了断言
    page.click(new_locator, timeout=timeout - HEAL_THRESHOLD_MS)
    _record_heal(old=locator, new=new_locator, desc=desc)
    logger.info(f"自修复成功: {locator} → {new_locator}")


# ============================================================
# 主流程：采集 → AI 认目标 → 代码造定位器 → 验证
# ============================================================

def heal_locator(page, old_locator: str, desc: str, error: Exception) -> str | None:
    snapshot = capture_snapshot(
        page, str(error), traceback.format_exc())

    # ---- 通道 A：AI 从层级树里认节点，代码造 role 定位器 ----
    for candidate in _ask_ai_by_tree(snapshot, old_locator, desc):
        if _verify(page, candidate):
            return candidate

    # ---- 通道 B：AI 在截图上指坐标，代码映射回 DOM 节点造定位器 ----
    point = _ask_ai_by_vision(snapshot, old_locator, desc)
    if point:
        candidate = _locator_from_point(page, *point)
        if candidate and _verify(page, candidate):
            return candidate

    logger.warning("自修复失败：AI 未给出通过验证的候选")
    return None


# ============================================================
# 通道 A：层级树 + AI 选节点
# ============================================================

def _ask_ai_by_tree(snapshot: dict, old_locator: str, desc: str) -> list[str]:
    """把 AX Tree/锚点子树给 AI，让它返回目标节点的 role+name。
    AI 只输出"节点指认"，定位器由本函数构造。"""
    prompt = f"""页面有一个元素定位失败，请从层级树中指认目标元素。

【元素意图】{desc or "未知，请结合旧定位器推断"}
【失效定位器】{old_locator}（其中的文本/class 仍是有效线索）
【出错代码】{(snapshot.get("error_line") or {}).get("code", "")}
【层级树】{json.dumps(snapshot.get("ax_tree") or snapshot.get("anchor_html"), ensure_ascii=False)[:6000]}

只返回 JSON：{{"role": "button|link|textbox|...", "name": "节点可见文本"}}
找不到就返回 {{"role": null}}"""
    try:
        resp = chat(prompt)
        data = json.loads(resp[resp.index("{"):resp.rindex("}") + 1])
        if not data.get("role"):
            return []
        # 代码构造定位器：优先 role+name（最稳），退回 text 匹配
        locators = [f'role={data["role"]}[name="{data["name"]}"]']
        if data.get("name"):
            locators.append(f'text={data["name"]}')
        return locators
    except Exception as e:
        logger.warning(f"AI 树通道异常: {e}")
        return []


# ============================================================
# 通道 B：截图 + AI 指坐标 → elementFromPoint 映射真实节点
# ============================================================

def _ask_ai_by_vision(snapshot: dict, old_locator: str, desc: str):
    """多模态 AI 看图指目标坐标（相对坐标 0~1）。
    需要视觉模型（doubao-vision 等），纯文本模型返回 None 自动跳过。"""
    if not snapshot.get("screenshot"):
        return None
    prompt = f"""这是一张网页截图，{desc or "目标元素见下"}。
失效定位器：{old_locator}
请指出目标元素在图中的中心位置，只返回 JSON：{{"x": 0.0~1.0, "y": 0.0~1.0}}"""
    try:
        resp = chat(prompt, image=snapshot["screenshot"])   # 视觉模型调用
        data = json.loads(resp[resp.index("{"):resp.rindex("}") + 1])
        return float(data["x"]), float(data["y"])
    except Exception:
        return None


def _locator_from_point(page, rel_x: float, rel_y: float) -> str | None:
    """视觉坐标 → 真实 DOM 节点 → 代码提取特征构造定位器（全程无 AI 文本）。"""
    js = """([rx, ry]) => {
      const el = document.elementFromPoint(
        rx * window.innerWidth, ry * window.innerHeight);
      if (!el) return null;
      return { id: el.id, role: el.getAttribute("role"),
               tag: el.tagName.toLowerCase(),
               text: (el.innerText || "").trim().slice(0, 50),
               aria: el.getAttribute("aria-label") };
    }"""
    try:
        node = page.evaluate(js, [rel_x, rel_y])
        if not node:
            return None
        # 按定位器优先级从节点特征构造：aria-label > role+text > text > #id(非动态)
        if node.get("aria"):
            return f'[aria-label="{node["aria"]}"]'
        if node.get("role") and node.get("text"):
            return f'role={node["role"]}[name="{node["text"]}"]'
        if node.get("text"):
            return f'text={node["text"]}'
        if node.get("id") and not any(ch.isdigit() for ch in node["id"][-4:]):
            return f'#{node["id"]}'        # 尾部带数字的 id 视为动态 id，不用
        return None
    except Exception:
        return None


# ============================================================
# 确定性验证 + heal 落库
# ============================================================

def _verify(page, locator: str) -> bool:
    """唯一且可见双条件——AI 候选的生死判官。"""
    try:
        loc = page.locator(locator)
        return loc.count() == 1 and loc.first.is_visible()
    except Exception:
        return False


def _record_heal(old: str, new: str, desc: str):
    """heal 记录落库（接 database.py 的 healing_record 表）。
    状态 healed，进入人工审核队列，审核通过才回写 page 源码。"""
    logger.info(f"[HEAL-RECORD] desc={desc} old={old} new={new}")
    # db.insert_heal_record(old_locator=old, new_locator=new,
    #                       desc=desc, status="healed", ...)
