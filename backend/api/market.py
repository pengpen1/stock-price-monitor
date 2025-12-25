"""
大盘市场 API

提供大盘指数、市场统计等端点
"""

from fastapi import APIRouter

router = APIRouter(tags=["大盘市场"])

# monitor 实例将在 main.py 中注入
monitor = None


def set_monitor(m):
    """注入 monitor 实例"""
    global monitor
    monitor = m


@router.get("/groups")
def get_groups():
    """获取所有分组"""
    return monitor.get_groups()


@router.post("/groups")
def add_group(data: dict):
    """添加分组"""
    return monitor.add_group(data.get("group", ""))


@router.delete("/groups/{group}")
def delete_group(group: str, delete_stocks: bool = False):
    """删除分组"""
    return monitor.delete_group(group, delete_stocks)


@router.get("/index/{code}/detail")
def get_index_detail(code: str):
    """获取指数详情"""
    return monitor.get_index_detail(code)


@router.get("/market/stats")
def get_market_stats():
    """获取市场统计"""
    return monitor.get_market_stats()


@router.get("/market/stats/history")
def get_market_stats_history(days: int = 30):
    """获取市场统计历史"""
    return monitor.get_market_stats_history(days)
