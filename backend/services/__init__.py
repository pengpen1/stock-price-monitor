"""
服务层模块

本模块包含各种业务服务：
- ai_service: AI 分析服务（支持多模型提供商）
"""

from .ai_service import AIService

__all__ = ["AIService"]
