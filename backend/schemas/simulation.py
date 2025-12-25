"""
实盘模拟相关数据模型
"""

from pydantic import BaseModel
from typing import Optional


class SimulationCreateRequest(BaseModel):
    """创建模拟请求"""
    stock_code: str
    stock_name: str
    total_days: int
    initial_capital: float = 1000000


class SimulationTradeRequest(BaseModel):
    """模拟交易请求"""
    session_id: str
    trade_type: str
    price: float = 0
    quantity: int = 0
    reason: str = ""
    current_date: str = ""


class SimulationAnalyzeRequest(BaseModel):
    """模拟分析请求"""
    session_id: str
    provider: str
    api_key: str
    model: str
    proxy: Optional[str] = None
