"""
设置管理 API

提供系统设置的获取和更新端点
"""

from fastapi import APIRouter

router = APIRouter(prefix="/settings", tags=["设置管理"])

# monitor 实例将在 main.py 中注入
monitor = None


def set_monitor(m):
    """注入 monitor 实例"""
    global monitor
    monitor = m


@router.get("")
def get_settings():
    """获取设置"""
    return monitor.get_settings()


@router.post("")
def update_settings(settings: dict):
    """更新设置"""
    return monitor.update_settings(settings)
