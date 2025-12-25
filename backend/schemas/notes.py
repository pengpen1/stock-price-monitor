"""
笔记相关数据模型
"""

from pydantic import BaseModel
from typing import Optional


class NoteRequest(BaseModel):
    """笔记请求"""
    filename: str
    content: Optional[str] = ""


class NoteUpdateRequest(BaseModel):
    """更新笔记请求"""
    content: str


class NoteRenameRequest(BaseModel):
    """重命名笔记请求"""
    new_name: str


class NoteConvertRequest(BaseModel):
    """笔记转换请求"""
    content: str
    provider: str
    api_key: str
    model: str
    proxy: Optional[str] = None
