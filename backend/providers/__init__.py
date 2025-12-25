"""
AI 模型提供商模块

本模块实现了多模型提供商的协议抽象，支持：
- OpenAI Compatible（OpenAI、DeepSeek、Kimi、通义千问、Grok）
- Google Gemini Native
- Anthropic Claude Native
- 字节豆包 Native
- 智谱 GLM Native

设计原则：
1. 以协议/API规范为第一维度，而非厂商
2. 统一的 ProviderConfig 配置结构
3. 协议映射 PROTOCOL_MAP
4. 厂商注册表 PROVIDER_REGISTRY
"""

from .config import ProviderConfig, PROVIDER_REGISTRY, get_provider_list
from .protocols import (
    BaseProtocol,
    OpenAICompatibleProtocol,
    GeminiProtocol,
    ClaudeProtocol,
    DoubaoProtocol,
    GLMProtocol,
    PROTOCOL_MAP,
    get_protocol,
)

__all__ = [
    "ProviderConfig",
    "PROVIDER_REGISTRY",
    "get_provider_list",
    "BaseProtocol",
    "OpenAICompatibleProtocol",
    "GeminiProtocol",
    "ClaudeProtocol",
    "DoubaoProtocol",
    "GLMProtocol",
    "PROTOCOL_MAP",
    "get_protocol",
]
