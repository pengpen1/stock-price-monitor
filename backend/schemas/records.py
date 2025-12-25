"""
交易记录相关数据模型
"""

from pydantic import BaseModel
from typing import Optional


class TradeRecordRequest(BaseModel):
    """交易记录请求"""
    stock_code: str
    stock_name: Optional[str] = None
    type: str  # B/S/T
    price: float
    quantity: int
    reason: str
    trade_time: Optional[str] = None
    mood: Optional[str] = "calm"
    level: Optional[int] = 2


class TradeRecordUpdateRequest(BaseModel):
    """更新交易记录请求"""
    type: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    reason: Optional[str] = None
    trade_time: Optional[str] = None
    mood: Optional[str] = None
    level: Optional[int] = None
    stock_name: Optional[str] = None


class ImportMdRequest(BaseModel):
    """导入 Markdown 请求"""
    content: str
