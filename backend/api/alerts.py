"""
预警管理 API

提供股票预警的设置、删除、触发查询等端点
"""

from fastapi import APIRouter

router = APIRouter(prefix="/alerts", tags=["预警管理"])

# monitor 实例将在 main.py 中注入
monitor = None


def set_monitor(m):
    """注入 monitor 实例"""
    global monitor
    monitor = m


@router.post("/{code}")
def set_alert(code: str, alert_config: dict):
    """设置预警"""
    return monitor.set_alert(code, alert_config)


@router.delete("/{code}")
def remove_alert(code: str):
    """移除预警"""
    return monitor.remove_alert(code)


@router.get("/triggered")
def get_triggered_alerts():
    """获取触发的预警"""
    return monitor.get_triggered_alerts()
