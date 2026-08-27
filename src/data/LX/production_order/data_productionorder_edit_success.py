import time
import random
from src.common.data_generator import DataGenerator

# 生产订单编辑测试数据
ProductionOrderEditData = {
    "menu_plan": "生产计划",
    "module_production_order": "生产订单",
    "iframe_name": "ProductionOrders",
    "add_button_name": "新 增",
    "order_number": DataGenerator().get_order_no("SCDD"),
    "initial_plan_quantity": "100",
    "edited_plan_quantity": "120",
    "query_button_name": "查询",
    "confirm_button_name": "确 定",
    "edit_button_name": "编 辑",
    "close_button_name": "close-circle",
    "today_text": "今天",
    "next_month_button": "下个月 (翻页下键)",
    "ms_id": "100100",
    "case_name": "productionorder_edit_success"
}