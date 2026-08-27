import time
import random
from src.common.data_generator import DataGenerator

# 生产订单编辑取消功能的数据

ProductionOrderEditCancelData = {
    "order_number": DataGenerator().get_order_no("SCDD"),
    "initial_plan_quantity": "100",
    "query_button_name": "查询",
    "edit_button_name": "编 辑",
    "close_button_name": "close",
    "today_text": "今天"
}
