import re
import json
import os
import yaml
from datetime import datetime
from playwright.sync_api import Playwright, sync_playwright


def logger_info(msg):
    print(f"[INFO] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}")


def logger_error(msg):
    print(f"[ERROR] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}")


def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "config", "execution_config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_materials_for_project(playwright, project_name, login_info):
    """获取指定项目的生效SOP物料信息"""
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    materials = []

    try:
        # 登录
        logger_info(f"开始登录 {project_name} 项目")
        page.goto(login_info["login_url"])
        page.get_by_role("textbox", name="请输入用户名").click()
        page.get_by_role("textbox", name="请输入用户名").fill(login_info["username"])
        page.get_by_role("textbox", name="请输入密码").click()
        page.get_by_role("textbox", name="请输入密码").fill(login_info["password"])
        page.get_by_role("textbox", name="请输入密码").press("Enter")
        page.wait_for_load_state("networkidle")
        logger_info(f"{project_name} 项目登录成功")

        # 导航到生产SOP页面
        logger_info(f"导航到 {project_name} 项目的生产SOP页面")
        page.get_by_role("listitem", name="产品管理").click()
        page.get_by_text("生产SOP").click()
        page.wait_for_load_state("networkidle")

        # 获取SOP iframe
        sop_frame = page.locator("iframe[name=\"ProductionSOP\"]").content_frame

        # 等待表格加载
        logger_info(f"等待 {project_name} 项目的表格加载...")
        sop_frame.locator("tbody.ant-table-tbody").wait_for()

        # 获取所有生效的物料信息
        page_num = 1

        while True:
            logger_info(f"正在处理 {project_name} 项目的第 {page_num} 页")

            # 等待表格加载
            page.wait_for_load_state("networkidle")
            sop_frame.locator("tbody.ant-table-tbody").wait_for()

            # 获取当前页所有行（排除测量行）
            rows = sop_frame.locator("tbody.ant-table-tbody tr.ant-table-row.ant-table-row-level-0")

            # 遍历每一行
            row_count = rows.count()
            logger_info(f"{project_name} 项目第 {page_num} 页共有 {row_count} 行数据")

            for i in range(row_count):
                row = rows.nth(i)

                # 获取所有列
                cells = row.locator("td")
                cell_count = cells.count()

                # 状态列在第8列（从1开始计数），对应索引7（从0开始）
                if cell_count >= 8:
                    status_cell = cells.nth(7)  # 第8列（从0开始）
                    status_text = status_cell.inner_text()

                    # 检查是否为生效状态
                    if "生效" in status_text:
                        # 物料编码列在第10列（从1开始计数），对应索引9（从0开始）
                        if cell_count >= 10:
                            material_cell = cells.nth(9)  # 第10列（从0开始）
                            material_text = material_cell.get_attribute("title")

                            # 从文本中提取物料编码，格式如 [MAT_xxx]物料_xxx
                            if material_text:
                                match = re.search(r'\[([^\]]+)\]', material_text)
                                if match:
                                    material_code = match.group(1)
                                    materials.append(material_code)
                                    logger_info(f"{project_name} 项目提取到生效物料: {material_code}")

            # 检查是否有下一页
            next_button = sop_frame.locator("li.ant-pagination-next")
            is_disabled = next_button.get_attribute("aria-disabled")

            if is_disabled == "true":
                logger_info(f"{project_name} 项目已到达最后一页，停止翻页")
                break

            # 点击下一页
            logger_info(f"{project_name} 项目点击下一页")
            next_button.click()
            page_num += 1

    except Exception as e:
        logger_error(f"{project_name} 项目执行出错: {str(e)}")
        raise
    finally:
        page.close()
        context.close()
        browser.close()

    return materials


def run(playwright: Playwright) -> None:
    """获取所有项目的生效SOP物料信息"""
    try:
        # 加载配置
        config = load_config()
        project_login = config.get("project_login", {})

        # 构建所有项目的物料信息
        all_projects_materials = {}
        update_time = datetime.now().strftime("%Y-%m-%d")

        # 遍历所有项目
        for project_name, login_info in project_login.items():
            logger_info(f"开始处理 {project_name} 项目")
            materials = get_materials_for_project(playwright, project_name, login_info)
            all_projects_materials[project_name] = {
                "materials": materials,
                "count": len(materials),
                "update_time": update_time
            }
            logger_info(f"{project_name} 项目共提取到 {len(materials)} 个生效物料")

        # 保存物料信息到文件
        save_dir = os.path.dirname(os.path.abspath(__file__))
        base_dir = os.path.dirname(save_dir)
        save_path = os.path.join(base_dir, "base", "sop_materials.py")

        with open(save_path, "w", encoding="utf-8") as f:
            f.write("#!/usr/bin/env python\n")
            f.write("# -*- coding: utf-8 -*-\n")
            f.write('"""SOP物料数据文件，由get_sop_material.py自动生成"""\n\n')
            f.write("SOP_MATERIALS = ")
            f.write(json.dumps(all_projects_materials, ensure_ascii=False, indent=4))
            f.write("\n")

        logger_info(f"所有项目的物料信息已保存到: {save_path}")

    except Exception as e:
        logger_error(f"脚本执行出错: {str(e)}")
        raise


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
