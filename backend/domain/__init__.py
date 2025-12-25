"""
业务领域层（Domain）

本模块包含核心业务逻辑，类似前端的 composables/hooks：
- stock_monitor: 股票监控核心逻辑
- stock_manager: 股票列表管理
- alert_manager: 预警管理
- records_manager: 交易记录管理
- simulation_manager: 模拟交易管理
- notes_manager: 笔记管理
"""

from .stock_monitor import StockMonitor
from .records_manager import RecordsManager
from .simulation_manager import SimulationManager
from .notes_manager import NotesManager

__all__ = [
    "StockMonitor",
    "RecordsManager",
    "SimulationManager",
    "NotesManager",
]
