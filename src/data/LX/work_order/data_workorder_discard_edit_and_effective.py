from src.common.data_generator import DataGenerator

# 生产工单新增、生效、勾选测试数据
WorkorderData = {
    # 导航栏数据
    "nav_production_management": "生产管理",
    "nav_production_workorder": "生产工单",
    # 主界面数据
    "main_iframe_name": "WorkOrder",
    # 工单数据
    "workorder_no_1": DataGenerator().get_order_no(),
    "workorder_no_2": DataGenerator().get_order_no(),
    "material_row_name": "MAT_1775196603_WQRS",
    "plan_qty": "100",
    # 元素索引数据（避免硬编码）
    "svg_material_index": 4,
    "div_second_select_index": 5,
    # 工单行号数据
    "row_no_1": "1",
    "row_no_2": "2"
}