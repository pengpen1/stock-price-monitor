"""
数据导入导出相关数据模型
"""

from pydantic import BaseModel
from typing import Optional, Dict


class ImportDataRequest(BaseModel):
    """导入数据请求"""
    stocks: Optional[Dict] = None
    settings: Optional[Dict] = None
    alerts: Optional[Dict] = None
