"""生成物料档案导入测试数据（基于实际模板字段顺序）"""
import openpyxl
from openpyxl.styles import Font, Alignment
import os

# 模板字段顺序（11列）：
# 物料编码 | 物料名称 | 物料规格 | 单位 | 物料来源 | 工艺路线 |
# 最高库存 | 最低库存 | 安全库存 | 备注 | yz数字（必填）

# 8 条测试数据（基于用户提供的实际数据，并补全模板的所有字段）
test_data = [
    # 物料编码,    物料名称,  物料规格,  单位,  物料来源, 工艺路线,           最高库存, 最低库存, 安全库存, 备注,            yz数字
    ["CPZXC001",  "自行车",  "标准型",  "辆",  "自制",   "自行车生产工艺路线", 100,     10,      20,      "自动化导入测试", 1],
    ["CPLT001",   "轮胎",    "26寸",    "个",  "自制",   "轮胎生产工艺路线",   200,     20,      30,      "自动化导入测试", 2],
    ["CPCJ001",   "车架",    "铝合金",  "个",  "自制",   "车架生产工艺路线",   150,     15,      25,      "自动化导入测试", 1],
    ["CPTB001",   "踏板",    "标准型",  "个",  "自制",   "踏板生产工艺路线",   200,     20,      30,      "自动化导入测试", 2],
    ["CPXJ001",   "橡胶",    "工业级",  "千克", "外采",  "—",                  500,     50,      100,     "自动化导入测试", 10],
    ["CPGS001",   "钢丝",    "2mm",     "米",  "外采",   "—",                  1000,    100,     200,     "自动化导入测试", 20],
    ["CPSJB001",  "塑胶板",  "5mm",     "片",  "外采",   "—",                  300,     30,      50,      "自动化导入测试", 4],
    ["CPJSG001",  "金属管",  "标准型",  "根",  "外采",   "—",                  200,     20,      40,      "自动化导入测试", 5],
]

# 输出路径
output_dir = "testdata"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "物料档案导入测试数据.xlsx")

# 创建工作簿
wb = openpyxl.Workbook()
ws = wb.active
ws.title = "数据"

# 写表头（与系统模板一致）
headers = [
    "物料编码", "物料名称", "物料规格", "单位", "物料来源", "工艺路线",
    "最高库存", "最低库存", "安全库存", "备注", "yz数字（必填）"
]
ws.append(headers)

# 表头加粗
for cell in ws[1]:
    cell.font = Font(bold=True)
    cell.alignment = Alignment(horizontal="center")

# 写数据
for row in test_data:
    ws.append(row)

# 保存
wb.save(output_path)
print(f"测试数据已生成: {os.path.abspath(output_path)}")
print(f"共 {len(test_data)} 条数据")
print(f"字段: {headers}")
