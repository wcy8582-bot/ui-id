import time
import random
from src.common.data_generator import DataGenerator

# 生成唯一的工单号和批次号
work_order_id = DataGenerator().get_order_no()
batch_no = DataGenerator().get_order_no("batch")

WorkorderData = {
    # 新增工单数据
    "work_order_id": work_order_id,
    "batch_no": batch_no,
    "product_row_name": "MAT_1775196603_WQRS",
    "planned_qty": "100",
    "remark": "FUZZY",
    
    # 模糊查询数据（为工单号和批次号的一部分）
    "work_order_id_fuzzy": work_order_id[-8:],
    "product_code_fuzzy": "WQRS",
    "product_name_error": "WRQS",
    "product_name_fuzzy": "WQRS",
    "batch_no_fuzzy": batch_no[-8:],
    
    # 详情页URL
    "detail_url": "http://10.30.22.45:8080/sop-web/#/sop/orderManage/detail?id=1342057309100000000&mode=view"
}