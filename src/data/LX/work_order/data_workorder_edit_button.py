import re
from src.common.data_generator import DataGenerator

# 生产工单编辑按钮测试数据
WorkorderEditButtonData = {
    # 主页面导航文本
    "production_management_text": "生产管理",
    "production_workorder_text": "生产工单",
    # 主iframe名称
    "main_iframe_name": "WorkOrder",
    # 按钮文本
    "add_button_text": "新 增",
    "edit_button_text": "编 辑",
    "confirm_button_text": "确 定",
    "save_button_text": "保 存",
    "search_button_text": "查询",
    # 表单标签
    "workorder_no_label": "* 工单号",
    "plan_qty_label": "* 计划产量",
    "search_workorder_no_label": "工单号 :",
    # 测试输入数据
    "workorder_no": DataGenerator().get_order_no(),
    "plan_qty": "100",
    "material_row_text": "3 MAT_1775196603_WQRS 物料_WQRS",
    # 超时时间（毫秒）
    "popup_timeout": 10000
}