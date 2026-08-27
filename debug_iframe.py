"""临时调试脚本：探测生产订单列表页的 iframe 结构"""
from playwright.sync_api import sync_playwright

URL = "https://poc02.iclouddemo.supcon.com/lingoWeb/"
out = open("debug_iframe_result.txt", "w", encoding="utf-8")

def log(msg):
    print(msg)
    out.write(str(msg) + "\n")
    out.flush()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    ctx = browser.new_context()
    page = ctx.new_page()
    page.goto(URL)
    page.wait_for_timeout(3000)

    # 登录
    page.get_by_role("textbox", name="请输入用户名").fill("admin")
    page.get_by_role("textbox", name="请输入密码").fill("Supcon@1304")
    page.get_by_role("checkbox", name="已阅读并同意隐私政策").check()
    page.get_by_role("button", name="登 录").click()
    page.wait_for_timeout(10000)
    log(f"登录后 URL: {page.url}")
    log(f"页面标题: {page.title()}")

    # 进入生产订单页面
    page.get_by_text("生产管理").click()
    page.wait_for_timeout(2000)
    page.get_by_text("生产订单").click()
    page.wait_for_timeout(8000)

    # 列出所有 iframe
    log("\n========== 所有 iframe ==========")
    frames = page.frames
    for i, f in enumerate(frames):
        log(f"[{i}] name={f.name!r} url={f.url}")

    # 用 frame_locator 试 supos-tab-framework-1
    log("\n========== 测试 frame_locator(supos-tab-framework-1) ==========")
    try:
        fl = page.frame_locator("iframe[name='supos-tab-framework-1']")
        btn = fl.get_by_role("button", name="重 置")
        log(f"重置按钮 count={btn.count()}")
        if btn.count() > 0:
            log(f"重置按钮可见: {btn.is_visible()}")
        tb = fl.get_by_role("textbox", name="生产订单编号 :")
        log(f"查询框 count={tb.count()}")
    except Exception as e:
        log(f"frame_locator 失败: {e}")

    # 也测试主页面是否直接能找到
    log("\n========== 测试主页面直接找 ==========")
    try:
        btn2 = page.get_by_role("button", name="重 置")
        log(f"主页重置按钮 count={btn2.count()}")
        tb2 = page.get_by_role("textbox", name="生产订单编号 :")
        log(f"主页查询框 count={tb2.count()}")
    except Exception as e:
        log(f"主页面测试失败: {e}")

    # 保存页面截图
    page.screenshot(path="debug_iframe.png", full_page=True)
    log("\n截图已保存: debug_iframe.png")

    # 测试查询按钮和表格内容
    log("\n========== 测试查询按钮和表格 ==========")
    try:
        search_btn = page.get_by_role("button", name="search 查询")
        log(f"查询按钮 count={search_btn.count()}")
        if search_btn.count() > 0:
            log(f"查询按钮可见: {search_btn.is_visible()}")
            log(f"查询按钮 enabled: {search_btn.is_enabled()}")
            # 打印按钮的 HTML
            btn_html = search_btn.evaluate("el => el.outerHTML")
            log(f"查询按钮 HTML: {btn_html}")
    except Exception as e:
        log(f"查询按钮测试失败: {e}")

    # 测试表格第一行内容
    try:
        first_row = page.locator(".ant-table-tbody tr.ant-table-row").first
        log(f"表格第一行 count={first_row.count()}")
        if first_row.count() > 0:
            cells = first_row.locator("td")
            log(f"第一行单元格数: {cells.count()}")
            for i in range(min(cells.count(), 8)):
                txt = cells.nth(i).inner_text()
                log(f"  第{i}列: {txt!r}")
    except Exception as e:
        log(f"表格测试失败: {e}")

    # 测试所有按钮
    log("\n========== 页面所有按钮 ==========")
    try:
        all_btns = page.get_by_role("button")
        log(f"按钮总数: {all_btns.count()}")
        for i in range(min(all_btns.count(), 15)):
            try:
                txt = all_btns.nth(i).inner_text()
                vis = all_btns.nth(i).is_visible()
                log(f"  按钮[{i}]: text={txt!r} visible={vis}")
            except:
                pass
    except Exception as e:
        log(f"按钮枚举失败: {e}")

    log("\n调试完成，10秒后关闭")
    page.wait_for_timeout(10000)
    browser.close()

out.close()
