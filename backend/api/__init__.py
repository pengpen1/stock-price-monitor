"""
API 路由层

本模块包含所有 API 路由定义，类似前端的 views 层
每个文件对应一组相关的 API 端点

路由分组：
- health: 健康检查
- stocks: 股票列表管理（/stocks）
- stock_detail: 单个股票详情（/stock）
- settings: 系统设置
- alerts: 预警管理
- market: 大盘市场
- ai: AI 分析
- records: 交易记录
- simulation: 模拟交易
- notes: 笔记管理
- data: 数据导入导出
"""

from .health import router as health_router
from .stocks import router as stocks_router
from .stock_detail import router as stock_detail_router
from .settings import router as settings_router
from .alerts import router as alerts_router
from .market import router as market_router
from .ai import router as ai_router
from .records import router as records_router
from .simulation import router as simulation_router
from .notes import router as notes_router
from .data import router as data_router

__all__ = [
    "health_router",
    "stocks_router",
    "stock_detail_router",
    "settings_router",
    "alerts_router",
    "market_router",
    "ai_router",
    "records_router",
    "simulation_router",
    "notes_router",
    "data_router",
]
