# -*- coding: utf-8 -*-
"""
erp_client.py —— 灵动小工单 ERP 接口客户端
==========================================
把你在 MeterSphere 里做的"登录 → 建供应商 → 建采购单 → 入库 → 查库存"
全流程，用代码重新表达一遍。MeterSphere 里的对应关系：

  MeterSphere                    本模块
  ─────────────────────────────────────────
  环境变量组（两套环境）    →    base_url / 账号从 config 读
  后置脚本提取 id           →    每个方法的 return（统一从 data 层解包）
  前置脚本注入关联参数       →    方法参数（supplier_id 等显式传参）
  场景步骤编排              →    tests_api/erp/ 下的测试函数

⚠️ 接入真实系统只需要做两件事：
  1. config 里填真实 base_url / 账号；
  2. 对照接口文档核对 ENDPOINTS 里的路径和字段名（此处为按 RESTful 习惯
     占位的合理猜测，字段名以真实接口返回为准）。
"""
import requests
from src.common.logger import logger


# ---------------------------------------------------------------------------
# 接口路径集中管理：真实系统的路径只改这一个地方，用例代码不动
# ---------------------------------------------------------------------------
ENDPOINTS = {
    "login":            "/api/login",                    # ⚠️ 核对
    # 基础资料
    "supplier_create":  "/api/base/supplier/create",     # ⚠️ 核对
    "supplier_delete":  "/api/base/supplier/delete",     # ⚠️ 核对
    "warehouse_create": "/api/base/warehouse/create",    # ⚠️ 核对
    # 采购管理
    "purchase_create":  "/api/purchase/order/create",    # ⚠️ 核对
    "purchase_audit":   "/api/purchase/order/audit",     # ⚠️ 核对
    "purchase_detail":  "/api/purchase/order/detail",    # ⚠️ 核对
    # 入库管理 / 库存
    "stock_in":         "/api/stock/in",                 # ⚠️ 核对
    "stock_query":      "/api/stock/query",              # ⚠️ 核对
}


class ErpApiError(Exception):
    """业务码非 0 时抛出，带业务码和消息，便于断言精确匹配"""
    def __init__(self, code, msg, payload):
        super().__init__(f"ERP 业务错误 code={code} msg={msg}")
        self.code, self.msg, self.payload = code, msg, payload


class ErpClient:
    """ERP 接口客户端：登录态一次获取全会话复用，业务码统一校验"""

    def __init__(self, base_url: str, username: str, password: str):
        self.base = base_url.rstrip("/")
        self.session = requests.Session()          # TCP 连接池 + cookie 复用
        self.session.headers["Content-Type"] = "application/json"
        self._login(username, password)

    # ------------------------------------------------------------------
    # 基础能力：登录 + 统一请求包装
    # ------------------------------------------------------------------
    def _login(self, username, password):
        r = self.session.post(self.base + ENDPOINTS["login"],
                              json={"username": username, "password": password},
                              timeout=10)
        data = r.json()
        token = data.get("data", {}).get("token")
        if not token:
            raise ErpApiError(data.get("code"), data.get("msg", "登录失败"), data)
        self.session.headers["Authorization"] = token
        logger.info("ERP 登录成功，token 已写入会话头")

    def _call(self, endpoint_key: str, method: str = "post",
              expect_ok: bool = True, **kwargs) -> dict:
        """统一请求入口：
        - 集中处理超时、HTTP 状态码、业务码
        - expect_ok=False 用于负向用例：预期业务失败时返回完整响应体给用例断言
        """
        url = self.base + ENDPOINTS[endpoint_key]
        r = self.session.request(method, url, timeout=10, **kwargs)
        assert r.status_code == 200, f"HTTP {r.status_code}: {url} {r.text[:200]}"
        data = r.json()
        if expect_ok and data.get("code") not in (0, 200):
            raise ErpApiError(data.get("code"), data.get("msg"), data)
        return data.get("data") if expect_ok else data

    # ------------------------------------------------------------------
    # 基础资料
    # ------------------------------------------------------------------
    def create_supplier(self, name: str, contact: str = "") -> str:
        data = self._call("supplier_create",
                          json={"name": name, "contact": contact})
        return data["id"]           # 后置提取： supplier_id

    def create_warehouse(self, name: str) -> str:
        data = self._call("warehouse_create", json={"name": name})
        return data["id"]

    def delete_supplier(self, supplier_id: str):
        self._call("supplier_delete", json={"id": supplier_id})

    # ------------------------------------------------------------------
    # 采购管理
    # ------------------------------------------------------------------
    def create_purchase_order(self, supplier_id: str, warehouse_id: str,
                              items: list, title: str = "") -> str:
        """items: [{"material": "螺丝", "qty": 100, "price": 0.5}]"""
        data = self._call("purchase_create", json={
            "supplierId": supplier_id,          # 前置注入：关联基础资料
            "warehouseId": warehouse_id,
            "title": title,
            "items": items,
        })
        return data["id"]           # 后置提取：采购单 id

    def audit_purchase_order(self, order_id: str, approve: bool = True):
        self._call("purchase_audit", json={"id": order_id, "approve": approve})

    def get_purchase_order(self, order_id: str) -> dict:
        return self._call("purchase_detail", method="get",
                          params={"id": order_id})

    # ------------------------------------------------------------------
    # 入库 / 库存
    # ------------------------------------------------------------------
    def stock_in(self, order_id: str):
        """按采购单入库"""
        return self._call("stock_in", json={"orderId": order_id})

    def stock_in_raw(self, **fields):
        """不入库链路的原始入库接口调用，负向/边界用例专用：
        直接传任意字段值（非数字、超长数字等），返回完整响应做断言。"""
        return self._call("stock_in", expect_ok=False, json=fields)

    def query_stock(self, warehouse_id: str, material: str) -> int:
        data = self._call("stock_query", method="get",
                          params={"warehouseId": warehouse_id, "material": material})
        return int(data["qty"])
