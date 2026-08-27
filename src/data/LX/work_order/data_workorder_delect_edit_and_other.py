import time
import random
from src.common.data_generator import DataGenerator

# 生产工单模糊查询测试数据

# 工单测试数据
WorkorderData = {
    "order_no_1": DataGenerator().get_order_no(),
    "order_no_2": DataGenerator().get_order_no(),
    "plan_qty": "100"
}