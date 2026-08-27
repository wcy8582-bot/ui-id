# -*- coding: utf-8 -*-
"""
DOM 精准供给选择器（dom_selector.py）

解决的问题：自修复喂 AI 的 DOM，给全量界面 = 大量噪声
（注意力稀释、token 爆炸、AI 在错误区域"煞有介事"地找元素）。
本模块把 DOM 供给做成【漏斗】而不是【水管】：

  L0 锚点剥离：失败定位器砍最后一两级 → 锚父容器 → outerHTML
      （范围最小最精准，祖先还在就用它）
  L1 线索打分：从失败定位器+意图描述里提取文本/属性片段，
      在页面里模糊匹配候选元素 → 取候选的祖父容器子树 → Top-3 合并
      （锚点剥离失效时用——整条祖先链都变了，但元素身上的
        文本/class 等"尸体线索"通常还在，按线索反向圈定邻域）
  L2 无障碍树：AX Tree 精简语义树
  L3 全量剪枝 DOM：最终兜底

  每一级都有字符预算（MAX_CHARS），超出截断并标记。
  命中即停：拿到 L0 就不再取 L1/L2/L3，控制总量=控制噪声。
"""
import json
import re

from src.common.dom_snapshot import (
    find_anchor_html, capture_ax_tree, capture_pruned_dom, _truncate_html)
from src.common.logger import logger

MAX_CHARS = 6000        # 喂 AI 的 DOM 总预算
TOP_K = 3               # 线索打分保留的候选数
GRANDPARENT_LEVELS = 2  # 候选元素向上取几层容器


# ============================================================
# L1 核心：从失败定位器和意图描述里提取"尸体线索"
# ============================================================

def extract_clues(failed_locator: str, desc: str = "") -> list[str]:
    """从失效定位器/意图描述里提取可用于模糊匹配的线索片段。

    定位器失效 ≠ 全部失效：id 可能变了，但 text、class、aria-label
    这些"尸体"通常还在，它们是反向圈定元素邻域的线索。
    """
    clues = []

    # css 形态：#id、.class、[attr="v"]、text=xxx
    clues += re.findall(r'\.([a-zA-Z][\w-]{2,})', failed_locator)      # .class
    clues += re.findall(r'\[(?:name|placeholder|aria-label)="([^"]+)"\]',
                        failed_locator)
    m = re.search(r'text=["\']?([^"\']+)', failed_locator)             # text=xxx
    if m:
        clues.append(m.group(1))
    m = re.search(r'#([\w-]+)', failed_locator)                        # #id
    if m and not m.group(1)[-3:].isdigit():   # 尾部纯数字 = 动态 id，不做线索
        clues.append(m.group(1))

    # xpath 形态：text()、@attr 值
    clues += re.findall(r'text\(\)\s*=\s*["\']([^"\']+)', failed_locator)
    clues += re.findall(r'@\w+=["\']([^"\']+)["\']', failed_locator)

    # get_by_* 形态：name="xxx"
    clues += re.findall(r'name=["\']([^"\']+)["\']', failed_locator)

    # 意图描述本身就是最强线索（取前两个词，避免整句噪声）
    if desc:
        clues.append(desc.strip()[:20])

    # 去重、去空、截断
    seen, out = set(), []
    for c in clues:
        c = c.strip()[:40]
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    logger.info(f"提取线索片段: {out}")
    return out


# ============================================================
# L1 核心：按线索在页面里打分，圈定候选邻域
# ============================================================

_FIND_CANDIDATES_JS = """
([clues, topK, upLevels]) => {
  const norm = s => (s || "").replace(/\\s+/g, "").toLowerCase();
  const results = [];

  // 只遍历"可能有定位价值"的元素
  const els = document.querySelectorAll(
    "button,a,input,select,textarea,[role],[aria-label],label,td,th,span,div");

  for (const el of els) {
    const text = norm(el.innerText && el.innerText.slice(0, 80));
    const attrs = norm([el.id, el.className, el.getAttribute("name"),
      el.getAttribute("placeholder"), el.getAttribute("aria-label"),
      el.getAttribute("role")].filter(Boolean).join(" "));
    const hay = text + "|" + attrs;

    let score = 0;
    for (const clue of clues) {
      const c = norm(clue);
      if (!c) continue;
      if (hay.includes(c)) score += 10;              // 命中（规范化后包含）
      else if (c.length > 3) {
        // 模糊分：线索的前半段命中（文本可能被微调过）
        const half = c.slice(0, Math.ceil(c.length / 2));
        if (half.length > 2 && hay.includes(half)) score += 4;
      }
    }
    if (score > 0) {
      // 可见性加权：隐藏节点没有修复价值
      const visible = !!(el.offsetWidth || el.offsetHeight);
      results.push({ score: visible ? score : Math.floor(score / 3), el });
    }
  }

  results.sort((a, b) => b.score - a.score);
  const top = results.slice(0, topK);
  const scores = top.map(r => r.score);

  // 每个候选向上取 N 层容器，导出 outerHTML
  const htmls = [];
  for (const { el } of top) {
    let container = el;
    for (let i = 0; i < upLevels && container.parentElement; i++)
      container = container.parentElement;
    const html = container.outerHTML;
    // 去重：容器互相包含时只保留更小的那个（更精准）
    if (!htmls.some(h => h.includes(html) || html.includes(h)))
      htmls.push(html);
  }
  return { htmls, scores };
}
"""


def select_by_clues(page, failed_locator: str, desc: str = "") -> tuple[str | None, list[int]]:
    """L1：线索打分圈定邻域。返回 (合并后的候选容器HTML, 各候选得分)。"""
    clues = extract_clues(failed_locator, desc)
    if not clues:
        return None, []
    try:
        result = page.evaluate(_FIND_CANDIDATES_JS,
                               [clues, TOP_K, GRANDPARENT_LEVELS])
    except Exception as e:
        logger.warning(f"线索打分失败: {e}")
        return None, []
    if not result["htmls"]:
        return None, []
    merged = "\n<!-- ===== 候选邻域分隔 ===== -->\n".join(result["htmls"])
    merged = _truncate_html(merged)
    logger.info(f"线索打分命中 {len(result['htmls'])} 个候选邻域，"
                f"得分 {result['scores']}，共 {len(merged)} 字符")
    return merged, result["scores"]


# ============================================================
# 漏斗主入口：逐级收窄，命中即停
# ============================================================

def select_dom_for_ai(page, failed_locator: str, desc: str = "") -> dict:
    """DOM 精准供给主入口。返回：
      {strategy, content, token_estimate, candidates_score}
    逐级尝试 L0→L1→L2→L3，任何一级产出有效内容即停止。
    """
    # L0：锚点剥离（祖先还活着 → 最精准）
    html, hit = find_anchor_html(page, failed_locator)
    if html:
        return _pack("anchor_subtree", html, anchor=hit)

    # L1：线索打分圈定邻域（祖先链变了，用"尸体线索"反向圈定）
    content, scores = select_by_clues(page, failed_locator, desc)
    if content:
        return _pack("clue_candidates", content, candidates_score=scores)

    # L2：无障碍树（语义最干净）
    ax = capture_ax_tree(page)
    if ax:
        return _pack("ax_tree", json.dumps(ax, ensure_ascii=False))

    # L3：全量剪枝 DOM（最后兜底）
    dom = capture_pruned_dom(page)
    return _pack("pruned_dom", dom or "<页面 DOM 采集失败>")


# ============================================================
# 合并策略（推荐主路）：锚点上溯 + 尸体线索，同时圈定，一次喂出
# ============================================================

def select_merged_dom(page, failed_locator: str, desc: str = "") -> dict:
    """合并式精准供给：不再 L0/L1 二选一，而是两路同时跑、合并去重。

    设计理由：
      - 锚点上溯（L0）给出的是"目标原来所在的位置"——位置线索；
      - 尸体线索打分（L1）给出的是"目标现在可能在的位置"——特征线索；
      两者取并集，AI 同时看到【原位置邻域】+【现位置候选】，
      覆盖面 > 任何单一路径，而总量仍被 MAX_CHARS 预算锁死。

      典型互补场景：
        * 元素没动但父链 class 变了  → L0 失效，L1 兜底；
        * 元素被搬到了页面别的卡片  → L0 给的是空壳旧位置，
          L1 的候选里才有真身，AI 对比两处即可识别"搬家"；
        * 只跑 L0 会漏掉搬家场景，只跑 L1 在打分圈错时无路可退，
          合并后两条证据链互相印证，这正是"精准"的来源。

    返回结构同 _pack，strategy 标记为 merged_*，便于审计日志
    区分本次修复依据的是哪条证据链。
    """
    sections: list[str] = []
    meta: dict = {}

    # 第一路：锚点上溯两级（原位置证据）
    anchor_html, anchor_hit = find_anchor_html(page, failed_locator)
    if anchor_html:
        sections.append(
            f"<!-- 【证据1】失效定位器的祖先容器（目标原位置），锚点: {anchor_hit} -->\n"
            + anchor_html)
        meta["anchor"] = anchor_hit

    # 第二路：尸体线索打分 Top-K（现位置候选证据）
    clue_html, scores = select_by_clues(page, failed_locator, desc)
    if clue_html:
        # 与第一路去重：候选若已包含在锚点容器内则不重复给（省预算）
        if not (anchor_html and clue_html in anchor_html):
            sections.append(
                f"<!-- 【证据2】按残留文字/属性反向圈定的候选邻域，"
                f"得分 {scores} -->\n" + clue_html)
        meta["candidates_score"] = scores

    if sections:
        return _pack("merged_anchor+clues", "\n\n".join(sections), **meta)

    # 两路都空（页面级变化：跳错页/整页重渲染）→ 语义地图兜底
    ax = capture_ax_tree(page)
    if ax:
        return _pack("merged_fallback_ax", json.dumps(ax, ensure_ascii=False))
    dom = capture_pruned_dom(page)
    return _pack("merged_fallback_dom", dom or "<页面 DOM 采集失败>")


def _pack(strategy: str, content: str, **extra) -> dict:
    content = content[:MAX_CHARS] if len(content) > MAX_CHARS else content
    pack = {
        "strategy": strategy,
        "content": content,
        "token_estimate": len(content) // 2,   # 粗估：中文≈1字1token，英文≈2字符1token
        **extra,
    }
    logger.info(f"DOM 供给策略: {strategy}，{len(content)} 字符")
    return pack
