"""
AI 模型协议抽象模块

本文件定义了各种 AI 模型 API 的协议实现：
1. BaseProtocol - 协议基类，定义统一接口
2. OpenAICompatibleProtocol - OpenAI 兼容协议（支持 OpenAI、DeepSeek、Kimi、千问、Grok）
3. GeminiProtocol - Google Gemini 原生协议
4. ClaudeProtocol - Anthropic Claude 原生协议
5. DoubaoProtocol - 字节豆包原生协议
6. GLMProtocol - 智谱 GLM 原生协议

每个协议实现两个核心方法：
- get_models(): 获取可用模型列表
- chat(): 调用模型进行对话
"""

import json
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

import requests
import urllib3

from .config import ProviderConfig, PROVIDER_REGISTRY

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 尝试导入 httpx（更好的代理支持）
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


# ========== 错误码映射 ==========
ERROR_MESSAGES = {
    429: "请求过于频繁，API 配额已用尽。请稍后再试或更换模型",
    401: "API Key 无效或已过期，请检查配置",
    403: "API Key 权限不足或被禁用",
    404: "模型不存在或 API 路径错误",
    500: "服务器内部错误，请稍后重试",
    503: "服务暂时不可用，请稍后重试",
}


class BaseProtocol(ABC):
    """
    协议基类
    
    所有协议实现都需要继承此类并实现以下方法：
    - get_models(): 获取模型列表
    - chat(): 调用模型对话
    """
    
    @staticmethod
    def _get_proxies(proxy: str = None) -> Optional[Dict]:
        """构建代理配置"""
        if not proxy:
            return None
        proxy = proxy.strip()
        if not proxy.startswith("http://") and not proxy.startswith("https://"):
            proxy = f"http://{proxy}"
        return {"http://": proxy, "https://": proxy}
    
    @staticmethod
    def _get_requests_proxies(proxy: str = None) -> Optional[Dict]:
        """构建 requests 库的代理配置"""
        if not proxy:
            return None
        proxy = proxy.strip()
        if not proxy.startswith("http://") and not proxy.startswith("https://"):
            proxy = f"http://{proxy}"
        return {"http": proxy, "https": proxy}
    
    @staticmethod
    def _make_request(method: str, url: str, proxy: str = None, **kwargs) -> Dict:
        """
        统一的 HTTP 请求方法
        
        优先使用 httpx（更好的代理和 SSL 支持），回退到 requests
        """
        timeout = kwargs.pop("timeout", 60)
        
        if HAS_HTTPX:
            proxy_url = None
            if proxy:
                proxy = proxy.strip()
                if not proxy.startswith("http://") and not proxy.startswith("https://"):
                    proxy_url = f"http://{proxy}"
                else:
                    proxy_url = proxy
            
            try:
                with httpx.Client(
                    proxy=proxy_url,
                    timeout=timeout,
                    verify=False,
                    follow_redirects=True,
                ) as client:
                    if method.upper() == "GET":
                        response = client.get(url, **kwargs)
                    else:
                        response = client.post(url, **kwargs)
                    response.raise_for_status()
                    return response.json()
            except httpx.HTTPStatusError as e:
                raise requests.exceptions.HTTPError(response=e.response)
            except httpx.ProxyError as e:
                raise requests.exceptions.ProxyError(str(e))
            except httpx.ConnectError as e:
                raise requests.exceptions.ConnectionError(str(e))
            except httpx.TimeoutException as e:
                raise requests.exceptions.Timeout(str(e))
        else:
            proxies = BaseProtocol._get_requests_proxies(proxy)
            if method.upper() == "GET":
                response = requests.get(url, proxies=proxies, timeout=timeout, verify=False, **kwargs)
            else:
                response = requests.post(url, proxies=proxies, timeout=timeout, verify=False, **kwargs)
            response.raise_for_status()
            return response.json()
    
    @abstractmethod
    def get_models(self, config: ProviderConfig, api_key: str, proxy: str = None) -> List[Dict]:
        """
        获取可用模型列表
        
        Args:
            config: 提供商配置
            api_key: API Key
            proxy: 代理地址
            
        Returns:
            模型列表 [{"id": "model-id", "name": "Model Name"}, ...]
        """
        pass
    
    @abstractmethod
    def chat(
        self,
        config: ProviderConfig,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        proxy: str = None,
    ) -> str:
        """
        调用模型进行对话
        
        Args:
            config: 提供商配置
            api_key: API Key
            model: 模型 ID
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            proxy: 代理地址
            
        Returns:
            模型回复文本
        """
        pass


class OpenAICompatibleProtocol(BaseProtocol):
    """
    OpenAI 兼容协议
    
    支持所有兼容 OpenAI API 格式的提供商：
    - OpenAI 官方
    - DeepSeek
    - Kimi (月之暗面)
    - 通义千问
    - Grok
    """
    
    def get_models(self, config: ProviderConfig, api_key: str, proxy: str = None) -> List[Dict]:
        """获取 OpenAI 兼容格式的模型列表"""
        try:
            url = f"{config.base_url}{config.models_endpoint}"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            data = self._make_request("GET", url, proxy=proxy, headers=headers, timeout=30)
            
            models = []
            for m in data.get("data", []):
                model_id = m.get("id", "")
                # 过滤掉非聊天模型（如 embedding、whisper 等）
                if any(kw in model_id.lower() for kw in ["embed", "whisper", "tts", "dall"]):
                    continue
                models.append({"id": model_id, "name": model_id})
            
            # 按名称排序
            models.sort(key=lambda x: x["id"])
            return models if models else config.default_models or []
            
        except Exception as e:
            logger.warning(f"获取模型列表失败 ({config.id}): {e}")
            return config.default_models or []
    
    def chat(
        self,
        config: ProviderConfig,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        proxy: str = None,
    ) -> str:
        """调用 OpenAI 兼容格式的聊天接口"""
        url = f"{config.base_url}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        
        res_json = self._make_request("POST", url, proxy=proxy, headers=headers, json=data, timeout=90)
        return res_json["choices"][0]["message"]["content"]


class GeminiProtocol(BaseProtocol):
    """
    Google Gemini 原生协议
    """
    
    def get_models(self, config: ProviderConfig, api_key: str, proxy: str = None) -> List[Dict]:
        """获取 Gemini 模型列表"""
        try:
            url = f"{config.base_url}/v1beta/models?key={api_key}"
            
            data = self._make_request("GET", url, proxy=proxy, timeout=30)
            
            models = []
            for m in data.get("models", []):
                name = m.get("name", "").replace("models/", "")
                display_name = m.get("displayName", name)
                # 只保留支持 generateContent 的模型
                methods = m.get("supportedGenerationMethods", [])
                if "generateContent" in methods:
                    models.append({"id": name, "name": display_name})
            
            return models if models else config.default_models or []
            
        except Exception as e:
            logger.warning(f"获取 Gemini 模型列表失败: {e}")
            return config.default_models or []
    
    def chat(
        self,
        config: ProviderConfig,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        proxy: str = None,
    ) -> str:
        """调用 Gemini 聊天接口"""
        if not model:
            model = "gemini-1.5-flash"
        
        url = f"{config.base_url}/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        # Gemini 使用 contents 格式
        full_prompt = f"{system_prompt}\n\nUser Request:\n{user_prompt}"
        data = {"contents": [{"parts": [{"text": full_prompt}]}]}
        
        res_json = self._make_request("POST", url, proxy=proxy, headers=headers, json=data, timeout=90)
        
        try:
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return f"Gemini 返回了无法解析的数据: {json.dumps(res_json)}"


class ClaudeProtocol(BaseProtocol):
    """
    Anthropic Claude 原生协议
    """
    
    def get_models(self, config: ProviderConfig, api_key: str, proxy: str = None) -> List[Dict]:
        """Claude 没有公开的模型列表 API，返回默认模型"""
        return config.default_models or []
    
    def chat(
        self,
        config: ProviderConfig,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        proxy: str = None,
    ) -> str:
        """调用 Claude 聊天接口"""
        url = f"{config.base_url}/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        data = {
            "model": model,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
            "max_tokens": 4096,
        }
        
        res_json = self._make_request("POST", url, proxy=proxy, headers=headers, json=data, timeout=90)
        return res_json["content"][0]["text"]


class DoubaoProtocol(BaseProtocol):
    """
    字节豆包原生协议
    
    豆包 API 基于 OpenAI 格式，但有一些差异：
    - 需要使用 endpoint_id 而非 model_id
    - 认证方式略有不同
    """
    
    def get_models(self, config: ProviderConfig, api_key: str, proxy: str = None) -> List[Dict]:
        """
        获取豆包模型列表
        
        注意：豆包的模型需要在控制台创建推理接入点后才能使用
        这里返回默认模型列表，用户需要填入自己的 endpoint_id
        """
        # 豆包需要用户自己创建 endpoint，这里返回默认模型作为参考
        return config.default_models or []
    
    def chat(
        self,
        config: ProviderConfig,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        proxy: str = None,
    ) -> str:
        """
        调用豆包聊天接口
        
        豆包使用 OpenAI 兼容格式，但 model 字段需要填入 endpoint_id
        """
        url = f"{config.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": model,  # 这里是 endpoint_id
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        
        res_json = self._make_request("POST", url, proxy=proxy, headers=headers, json=data, timeout=90)
        return res_json["choices"][0]["message"]["content"]


class GLMProtocol(BaseProtocol):
    """
    智谱 GLM 原生协议
    
    GLM API 基于 OpenAI 格式，但有一些差异：
    - 认证使用 JWT Token（由 API Key 生成）
    - 支持的参数略有不同
    """
    
    def _generate_token(self, api_key: str, exp_seconds: int = 3600) -> str:
        """
        生成 JWT Token
        
        智谱 API 需要使用 JWT Token 进行认证
        API Key 格式：{id}.{secret}
        """
        try:
            import jwt
            
            parts = api_key.split(".")
            if len(parts) != 2:
                # 如果不是 JWT 格式，直接返回原始 key
                return api_key
            
            key_id, secret = parts
            
            payload = {
                "api_key": key_id,
                "exp": int(time.time()) + exp_seconds,
                "timestamp": int(time.time() * 1000),
            }
            
            return jwt.encode(
                payload,
                secret,
                algorithm="HS256",
                headers={"alg": "HS256", "sign_type": "SIGN"},
            )
        except ImportError:
            # 如果没有安装 PyJWT，直接使用 API Key
            logger.warning("PyJWT 未安装，使用原始 API Key")
            return api_key
        except Exception as e:
            logger.warning(f"生成 JWT Token 失败: {e}")
            return api_key
    
    def get_models(self, config: ProviderConfig, api_key: str, proxy: str = None) -> List[Dict]:
        """获取 GLM 模型列表"""
        # GLM 没有公开的模型列表 API，返回默认模型
        return config.default_models or []
    
    def chat(
        self,
        config: ProviderConfig,
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        proxy: str = None,
    ) -> str:
        """调用 GLM 聊天接口"""
        url = f"{config.base_url}/chat/completions"
        
        # 生成 JWT Token
        token = self._generate_token(api_key)
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        
        res_json = self._make_request("POST", url, proxy=proxy, headers=headers, json=data, timeout=90)
        return res_json["choices"][0]["message"]["content"]


# ========== 协议映射表 ==========
PROTOCOL_MAP: Dict[str, BaseProtocol] = {
    "openai": OpenAICompatibleProtocol(),
    "gemini": GeminiProtocol(),
    "anthropic": ClaudeProtocol(),
    "doubao": DoubaoProtocol(),
    "glm": GLMProtocol(),
}


def get_protocol(protocol_name: str) -> Optional[BaseProtocol]:
    """
    根据协议名称获取协议实例
    
    Args:
        protocol_name: 协议名称（openai/gemini/anthropic/doubao/glm）
        
    Returns:
        协议实例或 None
    """
    return PROTOCOL_MAP.get(protocol_name)
