import time
import random
from src.common.data_generator import DataGenerator

# 工单审批至下发测试数据
WorkorderApprovalToEffectivenessData = {
    "workorder_no": DataGenerator().get_order_no(),
    "material_row_name": "MAT_1775196603_WQRS",
    "plan_qty": "100",
    "status_edit": "编辑"
}