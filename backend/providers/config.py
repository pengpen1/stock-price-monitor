"""
AI 模型提供商配置模块

本文件定义了：
1. ProviderConfig - 统一的提供商配置数据类
2. PROVIDER_REGISTRY - 所有支持的提供商注册表
3. get_provider_list - 获取前端展示用的提供商列表

支持的提供商：
- OpenAI (GPT)
- DeepSeek
- Kimi (月之暗面)
- 通义千问 (Qwen)
- Grok (xAI)
- Gemini (Google)
- Claude (Anthropic)
- 豆包 (字节跳动)
- GLM (智谱)
"""

from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class ProviderConfig:
    """
    AI 模型提供商配置
    
    Attributes:
        id: 提供商唯一标识，如 openai / deepseek / kimi
        label: UI 显示名称
        protocol: 协议类型 openai | gemini | anthropic | doubao | glm
        base_url: API 基础地址（OpenAI-compatible 必填）
        auth_type: 认证类型 bearer | api-key | custom-header
        key_prefix: API Key 前缀，如 sk- / sk-ant-（可选）
        models_endpoint: 获取模型列表的端点，如 /v1/models
        need_proxy: 是否需要代理访问
        key_placeholder: API Key 输入框占位符
        default_models: 默认模型列表（当无法获取时使用）
    """
    id: str
    label: str
    protocol: str
    base_url: Optional[str] = None
    auth_type: str = "bearer"
    key_prefix: Optional[str] = None
    models_endpoint: str = "/v1/models"
    need_proxy: bool = False
    key_placeholder: str = "请输入 API Key"
    default_models: Optional[List[Dict]] = None


# ========== 提供商注册表 ==========
# 按协议分组，便于维护

PROVIDER_REGISTRY: Dict[str, ProviderConfig] = {
    # ========== OpenAI Compatible 协议 ==========
    "openai": ProviderConfig(
        id="openai",
        label="OpenAI (GPT)",
        protocol="openai",
        base_url="https://api.openai.com",
        auth_type="bearer",
        key_prefix="sk-",
        models_endpoint="/v1/models",
        need_proxy=True,
        key_placeholder="sk-...",
        default_models=[
            {"id": "gpt-4o", "name": "GPT-4o"},
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"},
            {"id": "gpt-4", "name": "GPT-4"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"},
        ]
    ),
    
    "deepseek": ProviderConfig(
        id="deepseek",
        label="DeepSeek",
        protocol="openai",
        base_url="https://api.deepseek.com",
        auth_type="bearer",
        key_prefix="sk-",
        models_endpoint="/v1/models",
        need_proxy=False,
        key_placeholder="sk-...",
        default_models=[
            {"id": "deepseek-chat", "name": "DeepSeek Chat"},
            {"id": "deepseek-coder", "name": "DeepSeek Coder"},
            {"id": "deepseek-reasoner", "name": "DeepSeek Reasoner (R1)"},
        ]
    ),
    
    "kimi": ProviderConfig(
        id="kimi",
        label="Kimi (月之暗面)",
        protocol="openai",
        base_url="https://api.moonshot.cn",
        auth_type="bearer",
        key_prefix="sk-",
        models_endpoint="/v1/models",
        need_proxy=False,
        key_placeholder="sk-...",
        default_models=[
            {"id": "moonshot-v1-8k", "name": "Moonshot V1 8K"},
            {"id": "moonshot-v1-32k", "name": "Moonshot V1 32K"},
            {"id": "moonshot-v1-128k", "name": "Moonshot V1 128K"},
        ]
    ),
    
    "qwen": ProviderConfig(
        id="qwen",
        label="通义千问 (Qwen)",
        protocol="openai",
        base_url="https://dashscope.aliyuncs.com/compatible-mode",
        auth_type="bearer",
        key_prefix="sk-",
        models_endpoint="/v1/models",
        need_proxy=False,
        key_placeholder="sk-...",
        default_models=[
            {"id": "qwen-turbo", "name": "Qwen Turbo"},
            {"id": "qwen-plus", "name": "Qwen Plus"},
            {"id": "qwen-max", "name": "Qwen Max"},
            {"id": "qwen-max-longcontext", "name": "Qwen Max 长文本"},
        ]
    ),
    
    "grok": ProviderConfig(
        id="grok",
        label="Grok (xAI)",
        protocol="openai",
        base_url="https://api.x.ai",
        auth_type="bearer",
        key_prefix="xai-",
        models_endpoint="/v1/models",
        need_proxy=True,
        key_placeholder="xai-...",
        default_models=[
            {"id": "grok-beta", "name": "Grok Beta"},
            {"id": "grok-2-1212", "name": "Grok 2"},
        ]
    ),
    
    # ========== Google Gemini 协议 ==========
    "gemini": ProviderConfig(
        id="gemini",
        label="Gemini (Google)",
        protocol="gemini",
        base_url="https://generativelanguage.googleapis.com",
        auth_type="api-key",
        key_prefix=None,
        models_endpoint="/v1beta/models",
        need_proxy=True,
        key_placeholder="AIza...",
        default_models=[
            {"id": "gemini-1.5-flash", "name": "Gemini 1.5 Flash"},
            {"id": "gemini-1.5-flash-8b", "name": "Gemini 1.5 Flash 8B"},
            {"id": "gemini-1.5-pro", "name": "Gemini 1.5 Pro"},
            {"id": "gemini-2.0-flash-exp", "name": "Gemini 2.0 Flash (实验版)"},
        ]
    ),
    
    # ========== Anthropic Claude 协议 ==========
    "claude": ProviderConfig(
        id="claude",
        label="Claude (Anthropic)",
        protocol="anthropic",
        base_url="https://api.anthropic.com",
        auth_type="custom-header",  # 使用 x-api-key
        key_prefix="sk-ant-",
        models_endpoint=None,  # Claude 没有公开的模型列表 API
        need_proxy=True,
        key_placeholder="sk-ant-...",
        default_models=[
            {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet"},
            {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku"},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet"},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku"},
        ]
    ),
    
    # ========== 字节豆包协议 ==========
    "doubao": ProviderConfig(
        id="doubao",
        label="豆包 (字节跳动)",
        protocol="doubao",
        base_url="https://ark.cn-beijing.volces.com/api/v3",
        auth_type="bearer",
        key_prefix=None,
        models_endpoint="/models",
        need_proxy=False,
        key_placeholder="请输入 API Key",
        default_models=[
            {"id": "doubao-pro-32k", "name": "豆包 Pro 32K"},
            {"id": "doubao-pro-128k", "name": "豆包 Pro 128K"},
            {"id": "doubao-lite-32k", "name": "豆包 Lite 32K"},
            {"id": "doubao-lite-128k", "name": "豆包 Lite 128K"},
        ]
    ),
    
    # ========== 智谱 GLM 协议 ==========
    "glm": ProviderConfig(
        id="glm",
        label="GLM (智谱)",
        protocol="glm",
        base_url="https://open.bigmodel.cn/api/paas/v4",
        auth_type="bearer",
        key_prefix=None,
        models_endpoint="/models",
        need_proxy=False,
        key_placeholder="请输入 API Key",
        default_models=[
            {"id": "glm-4-plus", "name": "GLM-4 Plus"},
            {"id": "glm-4-0520", "name": "GLM-4"},
            {"id": "glm-4-air", "name": "GLM-4 Air"},
            {"id": "glm-4-airx", "name": "GLM-4 AirX"},
            {"id": "glm-4-flash", "name": "GLM-4 Flash"},
            {"id": "glm-4-long", "name": "GLM-4 Long"},
        ]
    ),
}


def get_provider_list() -> List[Dict]:
    """
    获取前端展示用的提供商列表
    
    Returns:
        提供商列表，包含 id、label、protocol、needProxy、keyPlaceholder 等字段
    """
    result = []
    for provider_id, config in PROVIDER_REGISTRY.items():
        result.append({
            "id": config.id,
            "label": config.label,
            "protocol": config.protocol,
            "needProxy": config.need_proxy,
            "keyPlaceholder": config.key_placeholder,
        })
    return result


def get_provider_config(provider_id: str) -> Optional[ProviderConfig]:
    """
    根据 ID 获取提供商配置
    
    Args:
        provider_id: 提供商 ID
        
    Returns:
        ProviderConfig 或 None
    """
    return PROVIDER_REGISTRY.get(provider_id)
