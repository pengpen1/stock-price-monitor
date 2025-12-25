"""
数据存储层（Repositories）

本模块负责数据的持久化存储，包括：
- 交易记录存储
- AI 分析记录存储
- 模拟会话存储
- 笔记存储

注意：当前实现使用 JSON 文件存储，后续可扩展为数据库
"""

from .records_repo import RecordsRepository
from .simulation_repo import SimulationRepository
from .notes_repo import NotesRepository

__all__ = [
    "RecordsRepository",
    "SimulationRepository",
    "NotesRepository",
]
