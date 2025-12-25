"""
AI 相关数据模型
"""

from pydantic import BaseModel
from typing import Optional, Dict


class ModelsRequest(BaseModel):
    """获取模型列表请求"""
    provider: str
    api_key: str
    proxy: Optional[str] = None


class AnalyzeRequest(BaseModel):
    """AI 分析请求"""
    code: str
    type: str  # fast | precise
    provider: str
    api_key: str
    model: str
    proxy: Optional[str] = None
    inputs: Optional[Dict] = {}
