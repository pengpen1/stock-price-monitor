"""
数据导入导出 API

提供配置数据的导入、导出、路径管理等端点
"""

from fastapi import APIRouter
from schemas.data import ImportDataRequest

router = APIRouter(prefix="/data", tags=["数据管理"])

# monitor 实例将在 main.py 中注入
monitor = None


def set_monitor(m):
    """注入 monitor 实例"""
    global monitor
    monitor = m


@router.get("/export")
def export_data():
    """导出配置数据"""
    return monitor.export_data()


@router.post("/import")
def import_data(req: ImportDataRequest):
    """导入配置数据"""
    return monitor.import_data(req.stocks, req.settings, req.alerts)


@router.get("/path")
def get_data_path():
    """获取数据存储路径"""
    return monitor.get_data_path()


@router.post("/path")
def set_data_path(data: dict):
    """设置数据存储路径"""
    return monitor.set_data_path(data.get("path", ""))
