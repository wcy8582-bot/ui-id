# -*- coding: utf-8 -*-
"""
自修复现场采集模块（dom_snapshot.py）

职责：定位失败发生时，采集"给 AI 看的现场三件套"：
  1. 失败定位器 + 出错行（从执行日志/traceback 解析）
  2. 层级树（优先 AX Tree 无障碍树，兜底剪枝 DOM）
  3. 页面截图

设计原则：
  - 采集永不搞挂主流程：任何一步失败都降级，最坏情况也能给出全量剪枝 DOM
  - 给 AI 的信息是"证据"不是"猜测"：锚点子树来自真实 DOM，不加工语义
  - 体积受控：任何输出都有大小上限，防止超 token
"""
import os
import re
import time
from datetime import datetime

from src.common.logger import logger

MAX_HTML_CHARS = 8000        # 锚点子树/全量 DOM 的字符上限
MAX_AX_DEPTH = 8             # 无障碍树最大深度
MAX_TEXT_LEN = 50            # 节点文本截断长度


# ============================================================
# 第 1 步：从执行日志里解析"失败定位器 + 出错行"
# ============================================================

def extract_failed_locator(error_message: str) -> str | None:
    """从 Playwright 超时错误中解析失败的定位器。

    支持的典型报错形态：
      Locator.click: Timeout 30000ms exceeded.
      waiting for locator("#el-id-2847 > div.submit-btn")
      waiting for get_by_role("button", name="提交")
    """
    patterns = [
        r'waiting for locator\("([^"]+)"\)',
        r"waiting for locator\('([^']+)'\)",
        r'waiting for (get_by_\w+\([^)]+\))',
        r'waiting for (locator\([^)]+\))',
    ]
    for p in patterns:
        m = re.search(p, error_message)
        if m:
            logger.info(f"解析出失败定位器: {m.group(1)}")
            return m.group(1)
    logger.warning("未能从错误信息中解析出定位器")
    return None


def extract_error_line(traceback_text: str) -> dict | None:
    """从 traceback 解析用例文件的出错行号和代码内容。

    返回: {"file": "src/testcase/...", "line": 47, "code": "bom_frame.get_by_role(...)"}
    """
    matches = re.findall(r'File "(.*?testcase.*?)", line (\d+)', traceback_text)
    if not matches:
        return None
    file_path, line_no = matches[-1]     # 取最后一帧 = 用例自己的代码行
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
        code = lines[int(line_no) - 1].strip()
        return {"file": file_path, "line": int(line_no), "code": code}
    except OSError:
        return {"file": file_path, "line": int(line_no), "code": ""}


# ============================================================
# 第 2 步：锚点剥离 —— 砍掉定位器最后一两级，定位父容器
# ============================================================

def strip_locator_candidates(locator: str) -> list[str]:
    """把失败定位器按层级砍掉最后一两段，生成祖先定位器候选。

    例: "#form > div.el-id-2847 > button.submit"
      → ["#form > div.el-id-2847", "#form"]

    注意：role/text 等语义定位器没有层级可砍（如 get_by_role），
    返回空列表，由调用方降级到 AX Tree 或全量 DOM。
    """
    # xpath 形态: //div[@id='a']/span/button
    if locator.startswith("//") or locator.startswith("xpath="):
        parts = re.split(r"(?=/[^/])", locator)
        return ["".join(parts[:-i]) for i in (1, 2) if len(parts) > i]

    # css 形态: 按 > 或空格组合器砍
    for sep in (" > ", ">"):
        if sep in locator:
            parts = locator.split(sep)
            return [sep.join(parts[:-i]) for i in (1, 2) if len(parts) > i]
    if " " in locator:
        parts = locator.split(" ")
        return [" ".join(parts[:-i]) for i in (1, 2) if len(parts) > i]
    return []


def find_anchor_html(scope, locator: str) -> tuple[str | None, str | None]:
    """在 scope（page 或 frame）里逐级尝试祖先定位器，返回锚点容器的 outerHTML。

    返回: (html 或 None, 命中的祖先定位器 或 None)
    """
    for ancestor in strip_locator_candidates(locator):
        try:
            loc = scope.locator(ancestor)
            if loc.count() == 1:
                html = loc.element_handle(timeout=2000).evaluate(
                    "el => el.outerHTML")
                html = _truncate_html(html)
                logger.info(f"锚点命中: {ancestor}（子树 {len(html)} 字符）")
                return html, ancestor
        except Exception:
            continue   # 这级锚不住，继续往上一级砍
    return None, None


# ============================================================
# 第 3 步：层级树采集 —— AX Tree 优先，剪枝 DOM 兜底
# ============================================================

def _prune_ax_node(node: dict, depth: int = 0) -> dict | None:
    """剪枝无障碍树：限深度、截断文本、只留定位相关字段。"""
    if depth > MAX_AX_DEPTH or not isinstance(node, dict):
        return None
    pruned = {"role": node.get("role"), "name": (node.get("name") or "")[:MAX_TEXT_LEN]}
    children = [c for c in
                (_prune_ax_node(ch, depth + 1) for ch in node.get("children", []))
                if c]
    if children:
        pruned["children"] = children
    # 丢掉无 role 无 name 的纯容器节点（没有定位价值）
    if not pruned["role"] and not children:
        return None
    return pruned


def capture_ax_tree(page) -> dict | None:
    """采集无障碍树（含 iframe 逐帧）。体积小、语义强，是喂 AI 的首选。"""
    try:
        tree = {"main": _prune_ax_node(page.accessibility.snapshot())}
        for frame in page.frames[1:]:      # page.frames[0] 是主文档
            try:
                tree[f"frame:{frame.name or frame.url[-40:]}"] = \
                    _prune_ax_node(frame.accessibility.snapshot())
            except Exception:
                tree[f"frame:{frame.name}"] = "<跨域或不可达，跳过>"
        return tree
    except Exception as e:
        logger.warning(f"AX Tree 采集失败: {e}")
        return None


_PRUNE_DOM_JS = """
(root) => {
  const MAX_DEPTH = %d, MAX_TEXT = %d;
  function walk(el, depth) {
    if (depth > MAX_DEPTH) return "";
    const tag = el.tagName ? el.tagName.toLowerCase() : "";
    if (["script","style","svg","noscript","link","meta"].includes(tag)) return "";
    // 只保留定位相关属性
    let attrs = "";
    for (const a of ["id","class","name","role","type","placeholder","aria-label"]) {
      const v = el.getAttribute && el.getAttribute(a);
      if (v) attrs += ` ${a}="${String(v).slice(0, 60)}"`;
    }
    const text = (el.childNodes.length === 1 && el.firstChild.nodeType === 3)
      ? el.firstChild.textContent.trim().slice(0, MAX_TEXT) : "";
    let children = "";
    for (const child of el.children) children += walk(child, depth + 1);
    if (!attrs && !text && !children) return "";   // 无定位价值节点直接丢弃
    return `<${tag}${attrs}>${text}${children}</${tag}>`;
  }
  return walk(root, 0);
}
""" % (MAX_AX_DEPTH * 2, MAX_TEXT_LEN)


def capture_pruned_dom(scope) -> str | None:
    """全量 DOM 剪枝兜底：JS 遍历，去非定位节点、截断属性、限深。"""
    try:
        html = scope.locator("body").element_handle(timeout=3000).evaluate(
            _PRUNE_DOM_JS)
        return _truncate_html(html)
    except Exception as e:
        logger.warning(f"剪枝 DOM 采集失败: {e}")
        return None


def _truncate_html(html: str) -> str:
    if len(html) > MAX_HTML_CHARS:
        return html[:MAX_HTML_CHARS] + "\n<!-- 已截断，原长度 %d 字符 -->" % len(html)
    return html


# ============================================================
# 主入口：采集三件套
# ============================================================

def capture_snapshot(page, error_message: str, traceback_text: str,
                     save_dir: str = "screenshots/heal") -> dict:
    """定位失败时的现场采集主入口。

    返回喂给 AI 的完整现场包：
      failed_locator / error_line / anchor_html / ax_tree / dom / screenshot / url
    任何单点失败都降级，保证返回可用的最小集合。
    """
    os.makedirs(save_dir, exist_ok=True)
    snapshot = {"captured_at": datetime.now().isoformat()}

    # 0. 等待页面进入稳定态（截图和 DOM 必须是"同一个世界"）
    try:
        page.wait_for_load_state("networkidle", timeout=8000)
    except Exception:
        logger.warning("页面 8s 内未到 networkidle，按当前状态采集")

    # 1. 失败定位器 + 出错行
    snapshot["failed_locator"] = extract_failed_locator(error_message)
    snapshot["error_line"] = extract_error_line(traceback_text)
    snapshot["url"] = page.url

    # 2. 截图（紧贴 DOM 采集之前，保证一致性）
    shot_path = os.path.join(
        save_dir, f"heal_{time.strftime('%Y%m%d_%H%M%S')}.png")
    try:
        page.screenshot(path=shot_path)
        snapshot["screenshot"] = shot_path
    except Exception as e:
        logger.warning(f"截图失败: {e}")

    # 3. 层级树：先试锚点子树（最精准），失败则 AX Tree，再失败全量剪枝 DOM
    anchor_html, hit = None, None
    if snapshot["failed_locator"]:
        # 主文档和每个 iframe 都试一遍锚点（iframe 改版场景）
        anchor_html, hit = find_anchor_html(page, snapshot["failed_locator"])
        if not anchor_html:
            for frame in page.frames[1:]:
                try:
                    anchor_html, hit = find_anchor_html(
                        frame, snapshot["failed_locator"])
                    if anchor_html:
                        snapshot["anchor_frame"] = frame.name
                        break
                except Exception:      # 跨域 frame 会抛异常，跳过
                    continue
    snapshot["anchor_html"] = anchor_html
    snapshot["anchor_locator"] = hit

    if not anchor_html:
        snapshot["ax_tree"] = capture_ax_tree(page)
    if not anchor_html and not snapshot.get("ax_tree"):
        snapshot["dom"] = capture_pruned_dom(page)

    logger.info(f"现场采集完成: anchor={'✓' if anchor_html else '✗'} "
                f"ax={'✓' if snapshot.get('ax_tree') else '✗'} "
                f"shot={'✓' if snapshot.get('screenshot') else '✗'}")
    return snapshot
