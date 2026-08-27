"""批量替换 material_creat -> material 的临时脚本"""
import os
import re

root = r"i:\新员工\UI自动化测试框架\auto_ui_ld_new-master\auto_ui_ld_new-master\src"
old = "from src.common.material_creat"
new = "from src.common.material"

count = 0
for dirpath, _, files in os.walk(root):
    for f in files:
        if not f.endswith(".py"):
            continue
        path = os.path.join(dirpath, f)
        with open(path, "r", encoding="utf-8") as fp:
            content = fp.read()
        if old in content:
            new_content = content.replace(old, new)
            with open(path, "w", encoding="utf-8") as fp:
                fp.write(new_content)
            count += 1
            print(f"Updated: {path}")

print(f"\nTotal updated: {count} files")
