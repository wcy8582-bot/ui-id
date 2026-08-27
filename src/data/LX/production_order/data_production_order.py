import time
import random
from src.common.data_generator import DataGenerator

ProductionOrderData = {
    "order_no": DataGenerator().get_order_no("SCDD"),
    "plan_quantity": "100",
    "remark": DataGenerator().get_random_string(10),
    "refer_data_index": 1
}