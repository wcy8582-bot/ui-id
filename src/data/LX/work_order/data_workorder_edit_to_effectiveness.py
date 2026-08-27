import time
import random
from src.common.data_generator import DataGenerator

# 主页面测试数据
MainPageData = {
    "production_management": "生产管理",
    "work_order": "生产工单"
}

# 生产工单列表页面测试数据
WorkOrderData = {
    "iframe_name": "WorkOrder",
    "btn_add": "新 增",
    "btn_query": "查询",
    "btn_effect": "生 效",
    "btn_abandon": "废 弃",
    "btn_cancel": "取 消",
    "btn_confirm": "确 定",
    "btn_save": "保 存",
    "query_wo_no_label": "工单号 :"
}

# 新增工单弹窗测试数据
AddModalData = {
    "wo_no_label": "* 工单号",
    "wo_no": DataGenerator().get_order_no(),
    "material_row_name": "MAT_1775196603_WQRS",
    "plan_qty_label": "* 计划产量",
    "plan_qty": "100"
}