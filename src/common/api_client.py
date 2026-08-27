# -*- coding: utf-8 -*-
"""
被测系统接口客户端（造数/清理/校验专用）

职责：UI 用例的前置数据通过接口快速构造，替代"UI 一步步点出来"。
原则：
  - 数据自造自清：每个 create 都有对应的 delete/close，由 fixture 保证执行
  - 锚点自持：业务标识（title/编号）由造数方生成，不依赖接口返回的 id 做 UI 查询
  - 登录态复用：token 只获取一次

注意：以下接口路径为示例占位，接入时按真实 ERP 接口文档替换 URL 和字段名。
（可用 Charles 抓包或在 MeterSphere 场景里拿到真实接口定义）
"""
import requests

from src.common.config_loader import config_loader
from src.common.logger import logger


class ApiClient:
    """被测系统的接口客户端：供用例造数/清理/校验使用"""

    def __init__(self, project: str):
        config = config_loader.get_config()
        login_info = config.get('project_login', {}).get(project, {})
        self.base = login_info.get('login_url', '').rstrip('/')
        self.session = requests.Session()

        # 登录态只获取一次，之后所有请求复用
        resp = self.session.post(
            f"{self.base}/api/login",
            json={"username": login_info.get('username'),
                  "password": login_info.get('password')},
            timeout=15,
        )
        self.token = resp.json()["data"]["token"]
        self.session.headers.update({"Authorization": self.token})
        logger.info(f"ApiClient 登录成功，project={project}")

    # ---------------- 供应商 ----------------
    def create_supplier(self, title: str) -> dict:
        """创建供应商，返回接口完整响应 data"""
        resp = self.session.post(
            f"{self.base}/api/supplier/create",
            json={"supplierName": title},   # 字段名按真实接口替换
            timeout=15,
        )
        logger.info(f"接口造数：供应商 {title}")
        return resp.json()["data"]

    def delete_supplier(self, supplier_id):
        self.session.post(f"{self.base}/api/supplier/delete",
                          json={"id": supplier_id}, timeout=15)

    # ---------------- 仓库 ----------------
    def create_warehouse(self, title: str) -> dict:
        resp = self.session.post(
            f"{self.base}/api/warehouse/create",
            json={"warehouseName": title},
            timeout=15,
        )
        logger.info(f"接口造数：仓库 {title}")
        return resp.json()["data"]

    def delete_warehouse(self, warehouse_id):
        self.session.post(f"{self.base}/api/warehouse/delete",
                          json={"id": warehouse_id}, timeout=15)

    # ---------------- 生产工单 ----------------
    def create_production_order(self, title: str, supplier_id, warehouse_id,
                                **fields) -> dict:
        """创建生产工单：供应商/仓库 id 由上游 fixture 动态传入，不写死"""
        payload = {
            "orderTitle": title,
            "supplierId": supplier_id,      # ← 来自 supplier fixture 的返回值
            "warehouseId": warehouse_id,    # ← 来自 warehouse fixture 的返回值
            **fields,
        }
        resp = self.session.post(f"{self.base}/api/production/create",
                                 json=payload, timeout=15)
        logger.info(f"接口造数：生产工单 {title}（供应商={supplier_id}，仓库={warehouse_id}）")
        return resp.json()["data"]

    def close_production_order(self, order_id):
        self.session.post(f"{self.base}/api/production/close",
                          json={"id": order_id}, timeout=15)
