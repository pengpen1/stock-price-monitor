import requests
import json
import time
import ssl
import certifi
from typing import Dict, Any, List, Optional
import logging
import urllib3

# 禁用 SSL 警告（代理环境下可能需要）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 错误码映射为友好提示
ERROR_MESSAGES = {
    429: "请求过于频繁，API 配额已用尽。请稍后再试或更换模型（推荐使用 gemini-1.5-flash）",
    401: "API Key 无效或已过期，请检查配置",
    403: "API Key 权限不足或被禁用",
    404: "模型不存在或 API 路径错误",
    500: "服务器内部错误，请稍后重试",
    503: "服务暂时不可用，请稍后重试",
}

# 尝试导入 httpx（更好的代理支持）
try:
    import httpx

    HAS_HTTPX = True
    logger.info("使用 httpx 库进行 HTTP 请求")
except ImportError:
    HAS_HTTPX = False
    logger.info("httpx 未安装，使用 requests 库")


class AIService:

    @staticmethod
    def _get_proxies(proxy: str = None) -> dict:
        """
        构建代理配置，确保格式正确
        """
        if not proxy:
            return None

        # 确保代理地址格式正确
        proxy = proxy.strip()
        if not proxy.startswith("http://") and not proxy.startswith("https://"):
            proxy = f"http://{proxy}"

        logger.info(f"使用代理: {proxy}")
        return {"http://": proxy, "https://": proxy}

    @staticmethod
    def _get_requests_proxies(proxy: str = None) -> dict:
        """
        构建 requests 库的代理配置
        """
        if not proxy:
            return None

        proxy = proxy.strip()
        if not proxy.startswith("http://") and not proxy.startswith("https://"):
            proxy = f"http://{proxy}"

        return {"http": proxy, "https": proxy}

    @staticmethod
    def _make_request(method: str, url: str, proxy: str = None, **kwargs) -> dict:
        """
        统一的 HTTP 请求方法，优先使用 httpx
        """
        timeout = kwargs.pop("timeout", 60)

        if HAS_HTTPX:
            # 使用 httpx（更好的代理和 SSL 支持）
            # 构建代理地址
            proxy_url = None
            if proxy:
                proxy = proxy.strip()
                if not proxy.startswith("http://") and not proxy.startswith("https://"):
                    proxy_url = f"http://{proxy}"
                else:
                    proxy_url = proxy

            try:
                with httpx.Client(
                    proxy=proxy_url,  # httpx 新版使用 proxy 而不是 proxies
                    timeout=timeout,
                    verify=False,  # 跳过 SSL 验证
                    follow_redirects=True,
                ) as client:
                    if method.upper() == "GET":
                        response = client.get(url, **kwargs)
                    else:
                        response = client.post(url, **kwargs)
                    response.raise_for_status()
                    return response.json()
            except httpx.HTTPStatusError as e:
                # 转换为类似 requests 的异常格式
                raise requests.exceptions.HTTPError(response=e.response)
            except httpx.ProxyError as e:
                raise requests.exceptions.ProxyError(str(e))
            except httpx.ConnectError as e:
                raise requests.exceptions.ConnectionError(str(e))
            except httpx.TimeoutException as e:
                raise requests.exceptions.Timeout(str(e))
        else:
            # 回退到 requests
            proxies = AIService._get_requests_proxies(proxy)
            if method.upper() == "GET":
                response = requests.get(
                    url, proxies=proxies, timeout=timeout, verify=False, **kwargs
                )
            else:
                response = requests.post(
                    url, proxies=proxies, timeout=timeout, verify=False, **kwargs
                )
            response.raise_for_status()
            return response.json()

    @staticmethod
    def get_models(provider: str, api_key: str, proxy: str = None) -> List[Dict]:
        """
        获取指定提供商的可用模型列表
        """
        try:
            if provider.lower() == "openai" or provider.lower() == "gpt":
                return AIService._get_openai_models(api_key, proxy)
            elif provider.lower() == "gemini":
                return AIService._get_gemini_models(api_key, proxy)
            elif provider.lower() == "claude":
                return AIService._get_claude_models(api_key, proxy)
            else:
                return []
        except Exception as e:
            logger.error(f"获取模型列表失败: {e}")
            return []

    @staticmethod
    def _get_openai_models(api_key: str, proxy: str = None) -> List[Dict]:
        """获取 OpenAI 模型列表"""
        url = "https://api.openai.com/v1/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        data = AIService._make_request(
            "GET", url, proxy=proxy, headers=headers, timeout=30
        )
        # 过滤出 GPT 相关模型
        models = []
        for m in data.get("data", []):
            model_id = m.get("id", "")
            if "gpt" in model_id.lower():
                models.append({"id": model_id, "name": model_id})
        # 按名称排序
        models.sort(key=lambda x: x["id"])
        return models

    @staticmethod
    def _get_gemini_models(api_key: str, proxy: str = None) -> List[Dict]:
        """获取 Gemini 模型列表"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        logger.info(f"请求 Gemini 模型列表，使用代理: {proxy}")
        data = AIService._make_request("GET", url, proxy=proxy, timeout=30)
        models = []
        for m in data.get("models", []):
            name = m.get("name", "").replace("models/", "")
            display_name = m.get("displayName", name)
            # 只保留支持 generateContent 的模型
            methods = m.get("supportedGenerationMethods", [])
            if "generateContent" in methods:
                models.append({"id": name, "name": display_name})
        return models

    @staticmethod
    def _get_claude_models(api_key: str, proxy: str = None) -> List[Dict]:
        """Claude 没有公开的模型列表 API，返回常用模型"""
        return [
            {"id": "claude-3-5-sonnet-20241022", "name": "Claude 3.5 Sonnet"},
            {"id": "claude-3-5-haiku-20241022", "name": "Claude 3.5 Haiku"},
            {"id": "claude-3-opus-20240229", "name": "Claude 3 Opus"},
            {"id": "claude-3-sonnet-20240229", "name": "Claude 3 Sonnet"},
            {"id": "claude-3-haiku-20240307", "name": "Claude 3 Haiku"},
        ]

    @staticmethod
    def _format_volume(vol: int) -> str:
        """格式化成交量为易读格式"""
        if vol >= 100000000:
            return f"{vol / 100000000:.2f}亿"
        elif vol >= 10000:
            return f"{vol / 10000:.2f}万"
        return str(vol)

    @staticmethod
    def format_data_for_prompt(
        basic: Dict,
        minute_data: List[Dict],
        kline_data: List[Dict],
        extra_info: Optional[Dict] = None,
        market_data: Optional[Dict] = None,
    ) -> str:
        """
        将股票数据格式化为 LLM 提示词，重点突出成交量信息
        """
        prompt_parts = []

        # 1. 基本信息
        prompt_parts.append(f"### 股票基本信息\n")
        prompt_parts.append(f"- 代码: {basic.get('code')}")
        prompt_parts.append(f"- 名称: {basic.get('name')}")
        prompt_parts.append(f"- 当前价: {basic.get('price')}")
        prompt_parts.append(f"- 涨跌幅: {basic.get('change_percent')}%")
        prompt_parts.append(f"- 今日最高: {basic.get('high')}")
        prompt_parts.append(f"- 今日最低: {basic.get('low')}")
        prompt_parts.append(f"- 昨收: {basic.get('pre_close')}")
        if basic.get("volume"):
            prompt_parts.append(
                f"- 成交量: {AIService._format_volume(int(float(basic.get('volume', 0))))}"
            )
        if basic.get("amount"):
            prompt_parts.append(
                f"- 成交额: {AIService._format_volume(int(float(basic.get('amount', 0))))}"
            )

        # 2. 用户附加信息（精准分析模式）
        if extra_info:
            prompt_parts.append(f"\n### 用户附加信息\n")
            if extra_info.get("cost_price"):
                prompt_parts.append(f"- 持仓成本: {extra_info['cost_price']}")
            if extra_info.get("position"):
                prompt_parts.append(f"- 持仓数量: {extra_info['position']}")
            if extra_info.get("take_profit"):
                prompt_parts.append(f"- 止盈位置: {extra_info['take_profit']}")
            if extra_info.get("stop_loss"):
                prompt_parts.append(f"- 止损位置: {extra_info['stop_loss']}")
            if extra_info.get("extra_text"):
                prompt_parts.append(
                    f"- 补充说明/新闻/政策: \n{extra_info['extra_text']}"
                )

        # 3. 日K线数据（重点展示成交量）
        prompt_parts.append(f"\n### 近期日K线数据（价量配合分析）\n")
        if kline_data:
            last_k = kline_data[-15:]  # 展示最近15天
            prompt_parts.append(
                f"最近 {len(last_k)} 个交易日数据 (共提供 {len(kline_data)} 天历史):"
            )

            # 计算平均成交量用于对比
            volumes = [k["volume"] for k in kline_data[-30:] if k.get("volume")]
            avg_volume = sum(volumes) / len(volumes) if volumes else 0

            header = "| 日期 | 开盘 | 收盘 | 最高 | 最低 | 涨跌幅 | 成交量 | 量比 |"
            prompt_parts.append(header)
            prompt_parts.append("|---|---|---|---|---|---|---|---|")

            prev_close = None
            if len(kline_data) > 15:
                prev_close = kline_data[-16]["close"]

            for k in last_k:
                change = ""
                if prev_close:
                    pct = ((k["close"] - prev_close) / prev_close) * 100
                    change = f"{pct:+.2f}%"
                prev_close = k["close"]

                vol = k.get("volume", 0)
                vol_ratio = f"{vol / avg_volume:.2f}" if avg_volume > 0 else "-"
                vol_str = AIService._format_volume(vol)

                prompt_parts.append(
                    f"| {k['date']} | {k['open']} | {k['close']} | {k['high']} | {k['low']} | {change} | {vol_str} | {vol_ratio} |"
                )

            # 成交量趋势分析
            recent_5_vol = (
                sum([k["volume"] for k in last_k[-5:]]) / 5 if len(last_k) >= 5 else 0
            )
            recent_10_vol = (
                sum([k["volume"] for k in last_k[-10:]]) / 10
                if len(last_k) >= 10
                else 0
            )

            prompt_parts.append(f"\n**成交量分析:**")
            prompt_parts.append(
                f"- 30日平均成交量: {AIService._format_volume(int(avg_volume))}"
            )
            prompt_parts.append(
                f"- 近5日平均成交量: {AIService._format_volume(int(recent_5_vol))}"
            )
            prompt_parts.append(
                f"- 近10日平均成交量: {AIService._format_volume(int(recent_10_vol))}"
            )

            if recent_5_vol > avg_volume * 1.5:
                prompt_parts.append(f"- ⚠️ 近期成交量明显放大，需关注")
            elif recent_5_vol < avg_volume * 0.5:
                prompt_parts.append(f"- ⚠️ 近期成交量明显萎缩")

        # 4. 分时数据（包含成交量）
        prompt_parts.append(f"\n### 近期分时走势（含成交量）\n")
        if minute_data:
            # 按日期分组
            dates = {}
            for m in minute_data:
                d = m["date"]
                if d not in dates:
                    dates[d] = []
                dates[d].append(m)

            # 只展示最近2天的分时数据
            sorted_dates = sorted(dates.keys(), reverse=True)[:2]

            for d in sorted(sorted_dates):
                items = dates[d]
                prompt_parts.append(f"#### 日期: {d}")

                # 计算当日成交量统计
                total_vol = sum([item.get("volume", 0) for item in items])
                prompt_parts.append(
                    f"当日总成交量: {AIService._format_volume(total_vol)}"
                )

                header = "| 时间 | 价格 | 均价 | 成交量 | 累计成交量 |"
                prompt_parts.append(header)
                prompt_parts.append("|---|---|---|---|---|")

                cumulative_vol = 0
                for i, item in enumerate(items):
                    vol = item.get("volume", 0)
                    cumulative_vol += vol
                    # 每15分钟采样一次，以及开盘和收盘
                    if i == 0 or i == len(items) - 1 or i % 15 == 0:
                        prompt_parts.append(
                            f"| {item['time']} | {item['price']} | {item.get('avg_price', '-')} | {AIService._format_volume(vol)} | {AIService._format_volume(cumulative_vol)} |"
                        )

        # 5. 大盘数据
        if market_data:
            prompt_parts.append(f"\n### 大盘环境\n")

            # 指数数据
            index_data = market_data.get("index", {})
            if index_data:
                prompt_parts.append("**主要指数:**")
                for code, idx in index_data.items():
                    if idx:
                        prompt_parts.append(
                            f"- {idx.get('name', code)}: {idx.get('price')} ({idx.get('change_percent')}%)"
                        )

        prompt_parts.append(f"\n### 分析要求\n")
        prompt_parts.append("请重点分析：")
        prompt_parts.append("1. 价量配合关系（放量上涨/缩量下跌等）")
        prompt_parts.append("2. 成交量异动情况")
        prompt_parts.append("3. 结合大盘环境判断个股走势")
        prompt_parts.append("4. 短期趋势判断")
        prompt_parts.append("5. 操作建议（买入/持有/卖出）")

        return "\n".join(prompt_parts)

    @staticmethod
    def call_llm(
        provider: str,
        api_key: str,
        model: str,
        prompt: str,
        proxy: str = None,
        max_retries: int = 3,
    ) -> str:
        """
        调用 LLM API，支持代理和重试机制
        """
        system_prompt = "你是一个专业的股票分析师，擅长技术面分析和基本面分析。请根据提供的股票数据，给出专业的趋势预测和操作建议。重点关注成交量变化与价格走势的配合关系。输出格式使用Markdown。"

        last_error = None
        for attempt in range(max_retries):
            try:
                if provider.lower() == "openai" or provider.lower() == "gpt":
                    return AIService._call_openai(
                        api_key, model, system_prompt, prompt, proxy
                    )
                elif provider.lower() == "gemini":
                    return AIService._call_gemini(
                        api_key, model, system_prompt, prompt, proxy
                    )
                elif provider.lower() == "claude":
                    return AIService._call_claude(
                        api_key, model, system_prompt, prompt, proxy
                    )
                else:
                    return f"不支持的模型提供商: {provider}"
            except requests.exceptions.HTTPError as e:
                last_error = e
                status_code = getattr(getattr(e, "response", None), "status_code", 0)

                # 获取友好错误提示
                friendly_msg = ERROR_MESSAGES.get(
                    status_code, f"HTTP 错误 {status_code}"
                )
                logger.error(
                    f"LLM调用失败 (尝试 {attempt + 1}/{max_retries}): {friendly_msg}"
                )

                # 429 错误需要等待后重试
                if status_code == 429 and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5  # 递增等待时间: 5s, 10s, 15s
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue

                # 其他错误直接返回友好提示
                return f"分析失败: {friendly_msg}"

            except requests.exceptions.ProxyError as e:
                last_error = e
                logger.error(f"代理连接失败: {e}")
                return (
                    f"分析失败: 代理连接失败，请检查代理地址是否正确（当前: {proxy}）"
                )

            except requests.exceptions.ConnectionError as e:
                last_error = e
                error_str = str(e)
                logger.error(f"连接失败: {e}")

                if "ProxyError" in error_str or "proxy" in error_str.lower():
                    return f"分析失败: 代理连接失败，请检查代理是否正常运行（当前: {proxy}）"
                elif "ConnectTimeout" in error_str:
                    return f"分析失败: 连接超时，请检查网络或代理配置"
                else:
                    return f"分析失败: 网络连接失败 - {error_str[:100]}"

            except requests.exceptions.Timeout:
                last_error = "请求超时"
                logger.error(f"LLM调用超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return "分析失败: 请求超时，请检查网络或代理配置"

            except Exception as e:
                last_error = e
                logger.error(f"LLM调用失败: {e}")
                return f"分析失败: {str(e)}"

        return f"分析失败: 重试 {max_retries} 次后仍然失败 - {last_error}"

    @staticmethod
    def _call_openai(
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        proxy: str = None,
    ) -> str:
        url = "https://api.openai.com/v1/chat/completions"
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
        res_json = AIService._make_request(
            "POST", url, proxy=proxy, headers=headers, json=data, timeout=90
        )
        return res_json["choices"][0]["message"]["content"]

    @staticmethod
    def _call_gemini(
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        proxy: str = None,
    ) -> str:
        if not model:
            model = "gemini-pro"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}

        full_prompt = f"{system_prompt}\n\nUser Request:\n{user_prompt}"

        data = {"contents": [{"parts": [{"text": full_prompt}]}]}

        logger.info(f"调用 Gemini API，模型: {model}，代理: {proxy}")
        res_json = AIService._make_request(
            "POST", url, proxy=proxy, headers=headers, json=data, timeout=90
        )
        try:
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "Gemini 返回了无法解析的数据: " + json.dumps(res_json)

    @staticmethod
    def _call_claude(
        api_key: str,
        model: str,
        system_prompt: str,
        user_prompt: str,
        proxy: str = None,
    ) -> str:
        url = "https://api.anthropic.com/v1/messages"
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

        res_json = AIService._make_request(
            "POST", url, proxy=proxy, headers=headers, json=data, timeout=90
        )
        return res_json["content"][0]["text"]
