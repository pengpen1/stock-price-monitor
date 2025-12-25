"""
数据模型定义（Schemas）

本模块定义所有 API 请求/响应的数据模型，类似前端的 types 层
使用 Pydantic 进行数据验证
"""

from .ai import AnalyzeRequest, ModelsRequest
from .records import TradeRecordRequest, TradeRecordUpdateRequest, ImportMdRequest
from .simulation import SimulationCreateRequest, SimulationTradeRequest, SimulationAnalyzeRequest
from .notes import NoteRequest, NoteUpdateRequest, NoteRenameRequest, NoteConvertRequest
from .data import ImportDataRequest

__all__ = [
    "AnalyzeRequest",
    "ModelsRequest",
    "TradeRecordRequest",
    "TradeRecordUpdateRequest",
    "ImportMdRequest",
    "SimulationCreateRequest",
    "SimulationTradeRequest",
    "SimulationAnalyzeRequest",
    "NoteRequest",
    "NoteUpdateRequest",
    "NoteRenameRequest",
    "NoteConvertRequest",
    "ImportDataRequest",
]
