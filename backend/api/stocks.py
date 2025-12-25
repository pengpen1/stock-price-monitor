"""
股票管理 API

提供股票列表管理、分组管理等端点
注意：单个股票的详情 API 在 stock_detail.py 中
"""

from fastapi import APIRouter

router = APIRouter(prefix="/stocks", tags=["股票管理"])

# monitor 实例将在 main.py 中注入
monitor = None


def set_monitor(m):
    """注入 monitor 实例"""
    global monitor
    monitor = m


@router.get("")
def get_stocks():
    """获取股票列表和数据"""
    return monitor.get_stocks()


@router.post("/{code}")
def add_stock(code: str):
    """添加股票"""
    return monitor.add_stock(code)


@router.delete("/{code}")
def remove_stock(code: str):
    """删除股票"""
    return monitor.remove_stock(code)


@router.post("/reorder")
def reorder_stocks(data: dict):
    """重新排序股票"""
    return monitor.reorder_stocks(data.get("stocks", []))


@router.post("/focus/{code}")
def set_focused_stock(code: str):
    """设置重点关注股票"""
    return monitor.set_focused_stock(code)


@router.post("/group/{code}")
def set_stock_group(code: str, data: dict):
    """设置股票分组"""
    return monitor.set_stock_group(code, data.get("group", ""))
