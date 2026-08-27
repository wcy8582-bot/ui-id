# -*- coding: utf-8 -*-
"""
repair_prompt.py —— 自修复的"精准提问"层
==========================================
设计哲学：
    全量 DOM 喂 AI = 让 AI 在 200KB 文本里做"填空题"，幻觉率极高；
    本模块把任务转成"选择题"：
        1. dom_selector 漏斗圈出候选容器 A/B/C（精准供给）；
        2. 本模块把候选编号、连同 AX 语义地图、失败线索、操作意图
           组装成强约束 Prompt（精准提问）；
        3. AI 只允许返回结构化 JSON：选了谁、用什么定位策略、理由；
        4. 返回后由代码做确定性验收（唯一且可见），不过验收不落盘
           （精准验收 —— 在 self_heal._verify 中实现）。

    AI 的角色被严格限定为"辨认目标"，构造定位器和判断对错都是代码的事。
    这是"修复成功率"的工程来源：不靠模型更聪明，靠任务被约束得更小。
"""
import json
import re


# ---------------------------------------------------------------------------
# Prompt 组装：选择题化
# ---------------------------------------------------------------------------

def build_repair_prompt(context: dict, failed_locator: str, intent: str) -> str:
    """
    把 dom_selector.select_dom_for_ai() 的产出组装成强约束 Prompt。

    参数:
        context        : select_dom_for_ai 的返回（anchor_html/candidates/
                         ax_tree/screenshot/page_state）
        failed_locator : 失败定位器原文（AI 的"寻人启事"）
        intent         : 本步骤的操作意图（如 "点击提交审核按钮"），
                         用于多个候选之间的消歧
    返回:
        完整 prompt 字符串
    """
    parts = []

    # ── 角色与任务：先框死 AI 的职责边界 ──────────────────────────
    parts.append(
        "你是 UI 自动化定位器修复助手。一个 Playwright 定位器失效了，"
        "你的唯一任务是：从下面给出的候选区域中，辨认出【用户本来想操作的元素】。\n"
        "禁止编造候选区域之外的信息；禁止输出解释性散文；只输出 JSON。"
    )

    # ── 寻人启事：失败定位器 + 操作意图 ───────────────────────────
    parts.append(
        f"【失效的定位器】\n{failed_locator}\n\n"
        f"【用户本步意图】\n{intent}\n"
        "注意：定位器失效通常是 class/text/DOM 层级变化，"
        "但定位器中的文字、角色(role)往往仍是寻找目标的最强线索。"
    )

    # ── 全局状态：先排除"页面都错了"的情况 ────────────────────────
    state = context.get("page_state") or {}
    if state:
        parts.append(
            f"【当前页面】url={state.get('url', '')} "
            f"title={state.get('title', '')}\n"
            "如果 url/title 表明当前页与意图无关（如跳转到了登录页/错误页），"
            "直接返回 {\"choice\": \"WRONG_PAGE\"}，不要强行选择。"
        )

    # ── 候选区：编号 A/B/C，AI 只需做选择 ─────────────────────────
    candidates = context.get("candidates") or []
    if candidates:
        block = ["【候选区域】（目标元素极大概率在其中一个之内）"]
        for i, html in enumerate(candidates):
            label = chr(ord("A") + i)
            block.append(f"--- 候选 {label} ---\n{html}")
        parts.append("\n".join(block))

    # ── 语义地图：AX Tree，候选都没中时的全页视角 ─────────────────
    ax = context.get("ax_tree")
    if ax:
        parts.append(
            "【全页语义地图】(无障碍树，仅含有语义的节点)\n"
            f"{ax}\n"
            "仅当所有候选区域都不含目标时，才允许从语义地图中选择，"
            "此时 choice 填 \"AX\"。"
        )

    # ── 输出契约：结构化、可解析、可验证 ──────────────────────────
    parts.append(
        "【输出格式】严格输出如下 JSON，不要输出任何其他内容：\n"
        "{\n"
        '  "choice": "A" | "B" | "C" | "AX" | "WRONG_PAGE" | "NOT_FOUND",\n'
        '  "strategy": "role" | "text" | "label" | "placeholder" | "testid",\n'
        '  "value": "用于定位的具体文字/名称",\n'
        '  "reason": "一句话说明为什么是它（将写入修复审计日志）"\n'
        "}\n"
        "要求：\n"
        "1. strategy 优先选 role（最抗前端重构），其次是 text/label；\n"
        "2. value 必须取自你所选区域中真实存在的文字，禁止改写或编造；\n"
        "3. 找不到可靠目标时返回 NOT_FOUND，宁可不修，不可猜修。"
    )

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# 应答解析：容错解析 AI 的 JSON，解析失败 = 本轮修复作废
# ---------------------------------------------------------------------------

def parse_ai_reply(raw: str) -> dict | None:
    """
    解析 AI 返回。AI 可能在 JSON 外面包裹 markdown 代码块或废话，
    这里做容错提取；提取不到合法结构就返回 None ——
    调用方（self_heal）收到 None 必须放弃本轮修复、保留原错误，
    绝不能拿半个解析结果去改代码。
    """
    if not raw:
        return None
    # 剥掉 ```json ... ``` 包裹
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None

    # 结构校验：缺关键字段 = 无效应答
    if data.get("choice") not in ("A", "B", "C", "AX", "WRONG_PAGE", "NOT_FOUND"):
        return None
    if data["choice"] in ("A", "B", "C", "AX"):
        if not data.get("strategy") or not data.get("value"):
            return None
    return data


# ---------------------------------------------------------------------------
# 定位器构造：AI 只出"策略+值"，拼代码是代码的事（确定性）
# ---------------------------------------------------------------------------

def build_locator_expression(reply: dict) -> str | None:
    """
    把 AI 的结构化应答翻译成 Playwright 定位表达式字符串。
    只允许白名单内的策略 —— AI 给别的策略一律拒绝，
    防止它输出 page.locator("第3个div的第2个span") 这类脆弱表达式。
    """
    strategy = reply.get("strategy")
    value = (reply.get("value") or "").replace('"', '\\"')
    if not value:
        return None
    table = {
        "role":        None,  # role 需要 name，单独处理
        "text":        f'page.get_by_text("{value}", exact=False)',
        "label":       f'page.get_by_label("{value}")',
        "placeholder": f'page.get_by_placeholder("{value}")',
        "testid":      f'page.get_by_test_id("{value}")',
    }
    if strategy == "role":
        # value 形如 "button:提交审核"（AI 按语义地图给出的 role:name）
        if ":" in value:
            role, name = value.split(":", 1)
            return f'page.get_by_role("{role.strip()}", name="{name.strip()}")'
        return None
    return table.get(strategy)
