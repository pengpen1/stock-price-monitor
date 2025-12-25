"""
AI 分析服务模块

本文件提供 AI 股票分析服务，支持多种模型提供商：
- OpenAI (GPT)
- DeepSeek
- Kimi (月之暗面)
- 通义千问 (Qwen)
- Grok (xAI)
- Gemini (Google)
- Claude (Anthropic)
- 豆包 (字节跳动)
- GLM (智谱)

主要功能：
1. get_models(): 获取指定提供商的可用模型列表
2. call_llm(): 调用 LLM 进行分析
3. call_llm_with_signal(): 调用 LLM 并返回结构化结果
4. format_data_for_prompt(): 格式化股票数据为提示词
"""

import json
import time
import logging
import re
from typing import Dict, Any, List, Optional

import requests

from providers import PROVIDER_REGISTRY, get_protocol, get_provider_list

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 错误码映射
ERROR_MESSAGES = {
    429: "请求过于频繁，API 配额已用尽。请稍后再试或更换模型",
    401: "API Key 无效或已过期，请检查配置",
    403: "API Key 权限不足或被禁用",
    404: "模型不存在或 API 路径错误",
    500: "服务器内部错误，请稍后重试",
    503: "服务暂时不可用，请稍后重试",
}


class AIService:
    """
    AI 分析服务
    
    提供统一的 AI 模型调用接口，支持多种提供商
    """
    
    @staticmethod
    def get_providers() -> List[Dict]:
        """
        获取所有支持的提供商列表
        
        Returns:
            提供商列表，用于前端展示
        """
        return get_provider_list()
    
    @staticmethod
    def get_models(provider: str, api_key: str, proxy: str = None) -> List[Dict]:
        """
        获取指定提供商的可用模型列表
        
        Args:
            provider: 提供商 ID（如 openai、deepseek、gemini 等）
            api_key: API Key
            proxy: 代理地址
            
        Returns:
            模型列表 [{"id": "model-id", "name": "Model Name"}, ...]
        """
        try:
            # 兼容旧的 provider 名称
            provider_id = provider.lower()
            if provider_id == "gpt":
                provider_id = "openai"
            
            # 获取提供商配置
            config = PROVIDER_REGISTRY.get(provider_id)
            if not config:
                logger.warning(f"未知的提供商: {provider}")
                return []
            
            # 获取协议实例
            protocol = get_protocol(config.protocol)
            if not protocol:
                logger.warning(f"未知的协议: {config.protocol}")
                return config.default_models or []
            
            # 调用协议获取模型列表
            return protocol.get_models(config, api_key, proxy)
            
        except Exception as e:
            logger.error(f"获取模型列表失败: {e}")
            return []
    
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
        调用 LLM API
        
        Args:
            provider: 提供商 ID
            api_key: API Key
            model: 模型 ID
            prompt: 用户提示词
            proxy: 代理地址
            max_retries: 最大重试次数
            
        Returns:
            模型回复文本
        """
        system_prompt = "你是一个专业的股票分析师，擅长技术面分析和基本面分析。请根据提供的股票数据，给出专业的趋势预测和操作建议。重点关注成交量变化与价格走势的配合关系。输出格式使用Markdown。"
        
        # 兼容旧的 provider 名称
        provider_id = provider.lower()
        if provider_id == "gpt":
            provider_id = "openai"
        
        # 获取提供商配置
        config = PROVIDER_REGISTRY.get(provider_id)
        if not config:
            return f"不支持的模型提供商: {provider}"
        
        # 获取协议实例
        protocol = get_protocol(config.protocol)
        if not protocol:
            return f"未知的协议: {config.protocol}"
        
        last_error = None
        for attempt in range(max_retries):
            try:
                return protocol.chat(config, api_key, model, system_prompt, prompt, proxy)
                
            except requests.exceptions.HTTPError as e:
                last_error = e
                status_code = getattr(getattr(e, "response", None), "status_code", 0)
                friendly_msg = ERROR_MESSAGES.get(status_code, f"HTTP 错误 {status_code}")
                logger.error(f"LLM调用失败 (尝试 {attempt + 1}/{max_retries}): {friendly_msg}")
                
                if status_code == 429 and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 5
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                return f"分析失败: {friendly_msg}"
                
            except requests.exceptions.ProxyError as e:
                return f"分析失败: 代理连接失败（当前: {proxy}）"
                
            except requests.exceptions.ConnectionError as e:
                error_str = str(e)
                if "ProxyError" in error_str or "proxy" in error_str.lower():
                    return f"分析失败: 代理连接失败"
                return f"分析失败: 网络连接失败"
                
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return "分析失败: 请求超时"
                
            except Exception as e:
                return f"分析失败: {str(e)}"
        
        return f"分析失败: 重试 {max_retries} 次后仍然失败"
    
    @staticmethod
    def call_llm_with_signal(
        provider: str,
        api_key: str,
        model: str,
        prompt: str,
        proxy: str = None,
        max_retries: int = 3,
        is_precise: bool = False,
        current_price: float = 0,
        future_dates: List[str] = None,
    ) -> Dict[str, Any]:
        """
        调用 LLM 并返回结构化结果
        
        Args:
            provider: 提供商 ID
            api_key: API Key
            model: 模型 ID
            prompt: 用户提示词
            proxy: 代理地址
            max_retries: 最大重试次数
            is_precise: 是否精准分析
            current_price: 当前价格
            future_dates: 未来日期列表
            
        Returns:
            {"result": str, "signal": str, "summary": str, "prediction": list}
        """
        # 构建结构化输出要求
        if is_precise and future_dates:
            structured_prompt = prompt + f"""

### 输出格式要求

请在分析结束后，额外输出一个 JSON 块，格式如下：
```json
{{
  "signal": "bullish/cautious/bearish",
  "summary": "一句话总结（50字以内）",
  "prediction": [
    {{"date": "{future_dates[0]}", "price": 预测价格, "change_pct": 相对当前价涨跌幅}},
    {{"date": "{future_dates[1]}", "price": 预测价格, "change_pct": 相对当前价涨跌幅}},
    {{"date": "{future_dates[2]}", "price": 预测价格, "change_pct": 相对当前价涨跌幅}},
    {{"date": "{future_dates[3]}", "price": 预测价格, "change_pct": 相对当前价涨跌幅}},
    {{"date": "{future_dates[4]}", "price": 预测价格, "change_pct": 相对当前价涨跌幅}}
  ]
}}
```

当前价格: {current_price}

signal 取值说明：
- bullish: 看涨，建议买入或持有
- cautious: 谨慎，建议观望
- bearish: 看跌，建议卖出或减仓

prediction 说明：
- 请根据技术分析和基本面分析，预测未来5个交易日的价格走势
- price: 预测的收盘价（保留2位小数）
- change_pct: 相对于当前价格的涨跌幅百分比（保留2位小数）
"""
        else:
            structured_prompt = prompt + """

### 输出格式要求

请在分析结束后，额外输出一个 JSON 块，格式如下：
```json
{
  "signal": "bullish/cautious/bearish",
  "summary": "一句话总结（50字以内）"
}
```

signal 取值说明：
- bullish: 看涨，建议买入或持有
- cautious: 谨慎，建议观望
- bearish: 看跌，建议卖出或减仓
"""
        
        # 调用 LLM
        result = AIService.call_llm(provider, api_key, model, structured_prompt, proxy, max_retries)
        
        # 检查是否失败
        if result.startswith("分析失败"):
            return {
                "result": result,
                "signal": "cautious",
                "summary": "",
                "prediction": []
            }
        
        # 提取信号
        signal_data = AIService.extract_signal_from_result(result)
        
        # 提取预测数据
        prediction = []
        if is_precise and current_price > 0:
            prediction = AIService.extract_prediction_from_result(result, current_price)
        
        return {
            "result": result,
            "signal": signal_data["signal"],
            "summary": signal_data["summary"],
            "prediction": prediction
        }
    
    @staticmethod
    def extract_signal_from_result(result: str) -> Dict[str, str]:
        """
        从分析结果中提取信号和摘要
        
        Args:
            result: LLM 返回的分析结果
            
        Returns:
            {"signal": "bullish/cautious/bearish", "summary": "..."}
        """
        # 尝试从结果中提取 JSON 块
        json_pattern = r'```json\s*(\{[^`]+\})\s*```'
        match = re.search(json_pattern, result, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                return {
                    "signal": data.get("signal", "cautious"),
                    "summary": data.get("summary", "")[:100]
                }
            except:
                pass
        
        # 尝试直接解析 JSON
        json_inline = r'\{\s*"signal"\s*:\s*"(\w+)"\s*,\s*"summary"\s*:\s*"([^"]+)"\s*\}'
        match = re.search(json_inline, result)
        if match:
            return {
                "signal": match.group(1),
                "summary": match.group(2)[:100]
            }
        
        # 关键词匹配作为后备方案
        result_lower = result.lower()
        signal = "cautious"
        
        bullish_keywords = ["看涨", "买入", "强势", "突破", "上涨", "bullish", "buy", "建议买入", "逢低买入"]
        bearish_keywords = ["看跌", "卖出", "弱势", "下跌", "bearish", "sell", "建议卖出", "减仓"]
        
        bullish_count = sum(1 for kw in bullish_keywords if kw in result_lower)
        bearish_count = sum(1 for kw in bearish_keywords if kw in result_lower)
        
        if bullish_count > bearish_count + 1:
            signal = "bullish"
        elif bearish_count > bullish_count + 1:
            signal = "bearish"
        
        # 提取摘要
        lines = [l.strip() for l in result.split('\n') if l.strip() and not l.startswith('#')]
        summary = lines[0][:100] if lines else "分析完成"
        
        return {"signal": signal, "summary": summary}
    
    @staticmethod
    def extract_prediction_from_result(result: str, current_price: float) -> List[Dict]:
        """
        从分析结果中提取价格预测数据
        
        Args:
            result: LLM 返回的分析结果
            current_price: 当前价格
            
        Returns:
            [{"date": "2025-12-16", "price": 44.5, "change_pct": 2.2}, ...]
        """
        # 尝试从结果中提取 prediction JSON 块
        json_pattern = r'```json\s*(\{[^`]*"prediction"[^`]*\})\s*```'
        match = re.search(json_pattern, result, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(1))
                if "prediction" in data and isinstance(data["prediction"], list):
                    return data["prediction"]
            except:
                pass
        
        # 尝试匹配独立的 prediction 数组
        pred_pattern = r'"prediction"\s*:\s*\[(.*?)\]'
        match = re.search(pred_pattern, result, re.DOTALL)
        if match:
            try:
                pred_str = "[" + match.group(1) + "]"
                predictions = json.loads(pred_str)
                if predictions:
                    return predictions
            except:
                pass
        
        return []
    
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
        trade_history: Optional[List[Dict]] = None,
        ai_history: Optional[List[Dict]] = None,
        money_flow: Optional[List[Dict]] = None,
        money_flow_days: int = 2,
        extra_data: Optional[Dict] = None,
        dragon_tiger: Optional[List[Dict]] = None,
    ) -> str:
        """
        将股票数据格式化为 LLM 提示词
        
        重点突出成交量和资金流向信息，包含用户交易记录和历史 AI 分析记录
        
        Args:
            basic: 股票基本信息
            minute_data: 分时数据
            kline_data: K线数据
            extra_info: 用户附加信息（持仓成本、止盈止损等）
            market_data: 大盘数据
            trade_history: 用户交易记录
            ai_history: 历史 AI 分析记录
            money_flow: 资金流向数据
            money_flow_days: 资金流向天数
            extra_data: 额外数据（换手率、量比、均线等）
            dragon_tiger: 龙虎榜数据
            
        Returns:
            格式化后的提示词
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
            prompt_parts.append(f"- 成交量: {AIService._format_volume(int(float(basic.get('volume', 0))))}")
        if basic.get("amount"):
            prompt_parts.append(f"- 成交额: {AIService._format_volume(int(float(basic.get('amount', 0))))}")
        
        # 1.1 技术面数据
        if extra_data:
            prompt_parts.append(f"\n### 技术面指标\n")
            if extra_data.get("turnover_rate") is not None:
                prompt_parts.append(f"- 换手率: {extra_data['turnover_rate']}%")
            if extra_data.get("volume_ratio") is not None:
                prompt_parts.append(f"- 量比: {extra_data['volume_ratio']:.2f}")
            if extra_data.get("amplitude") is not None:
                prompt_parts.append(f"- 振幅: {extra_data['amplitude']:.2f}%")
            
            # 均线数据
            ma_parts = []
            if extra_data.get("ma5"):
                ma_parts.append(f"MA5={extra_data['ma5']}")
            if extra_data.get("ma10"):
                ma_parts.append(f"MA10={extra_data['ma10']}")
            if extra_data.get("ma20"):
                ma_parts.append(f"MA20={extra_data['ma20']}")
            if extra_data.get("ma60"):
                ma_parts.append(f"MA60={extra_data['ma60']}")
            if ma_parts:
                prompt_parts.append(f"- 均线: {', '.join(ma_parts)}")
            
            # 基本面数据
            prompt_parts.append(f"\n### 基本面数据\n")
            if extra_data.get("pe_ratio") is not None:
                prompt_parts.append(f"- 市盈率(PE): {extra_data['pe_ratio']:.2f}")
            if extra_data.get("pb_ratio") is not None:
                prompt_parts.append(f"- 市净率(PB): {extra_data['pb_ratio']:.2f}")
            if extra_data.get("total_mv"):
                prompt_parts.append(f"- 总市值: {AIService._format_volume(int(extra_data['total_mv']))}")
            if extra_data.get("circ_mv"):
                prompt_parts.append(f"- 流通市值: {AIService._format_volume(int(extra_data['circ_mv']))}")
            if extra_data.get("industry"):
                prompt_parts.append(f"- 所属行业: {extra_data['industry']}")
        
        # 龙虎榜数据
        if dragon_tiger:
            prompt_parts.append(f"\n### 龙虎榜（近期异动）\n")
            prompt_parts.append("| 日期 | 上榜原因 | 涨跌幅 | 换手率 | 净买入 |")
            prompt_parts.append("|---|---|---|---|---|")
            for item in dragon_tiger:
                net_buy = AIService._format_volume(int(item.get("net_buy", 0))) if item.get("net_buy") else "-"
                prompt_parts.append(
                    f"| {item['date']} | {item.get('reason', '-')} | "
                    f"{item.get('change_pct', '-')}% | {item.get('turnover_rate', '-')}% | {net_buy} |"
                )
        
        # 2. 用户附加信息
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
                prompt_parts.append(f"- 补充说明: \n{extra_info['extra_text']}")
        
        # 3. 日K线数据
        prompt_parts.append(f"\n### 近期日K线数据\n")
        if kline_data:
            last_k = kline_data[-15:]
            prompt_parts.append(f"最近 {len(last_k)} 个交易日数据:")
            
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
        
        # 4. 大盘数据
        if market_data:
            prompt_parts.append(f"\n### 大盘环境\n")
            index_data = market_data.get("index", {})
            if index_data:
                prompt_parts.append("**主要指数:**")
                for code, idx in index_data.items():
                    if idx:
                        prompt_parts.append(
                            f"- {idx.get('name', code)}: {idx.get('price')} ({idx.get('change_percent')}%)"
                        )
        
        # 5. 用户交易记录
        if trade_history:
            prompt_parts.append(f"\n### 用户交易记录\n")
            prompt_parts.append("| 时间 | 类型 | 价格 | 手数 | 操作原因 |")
            prompt_parts.append("|---|---|---|---|---|")
            for t in trade_history:
                type_map = {"B": "买入", "S": "卖出", "T": "做T"}
                type_str = type_map.get(t["type"], t["type"])
                prompt_parts.append(
                    f"| {t['trade_time']} | {type_str} | {t['price']} | {t['quantity']} | {t['reason']} |"
                )
        
        # 6. 历史 AI 分析记录
        if ai_history:
            prompt_parts.append(f"\n### 历史 AI 分析记录\n")
            prompt_parts.append("| 时间 | 信号 | 摘要 |")
            prompt_parts.append("|---|---|---|")
            signal_map = {"bullish": "看涨📈", "cautious": "谨慎⚠️", "bearish": "看跌📉"}
            for a in ai_history:
                signal_str = signal_map.get(a["signal"], a["signal"])
                prompt_parts.append(f"| {a['datetime']} | {signal_str} | {a['summary']} |")
        
        # 7. 资金流向数据
        if money_flow:
            prompt_parts.append(f"\n### 资金流向（最近{money_flow_days}天）\n")
            
            daily_flow = {}
            for item in money_flow:
                time_str = item.get("time", "")
                date = time_str.split(" ")[0] if " " in time_str else time_str[:10]
                if date not in daily_flow:
                    daily_flow[date] = {"main_in": 0, "big_in": 0, "mid_in": 0, "small_in": 0, "super_in": 0}
                daily_flow[date]["main_in"] += item.get("main_in", 0)
                daily_flow[date]["big_in"] += item.get("big_in", 0)
                daily_flow[date]["mid_in"] += item.get("mid_in", 0)
                daily_flow[date]["small_in"] += item.get("small_in", 0)
                daily_flow[date]["super_in"] += item.get("super_in", 0)
            
            sorted_dates = sorted(daily_flow.keys(), reverse=True)[:money_flow_days]
            
            if sorted_dates:
                prompt_parts.append("| 日期 | 主力净流入 | 超大单 | 大单 | 中单 | 小单 |")
                prompt_parts.append("|---|---|---|---|---|---|")
                
                for date in sorted(sorted_dates):
                    flow = daily_flow[date]
                    main_net = flow["super_in"] + flow["big_in"]
                    prompt_parts.append(
                        f"| {date} | {AIService._format_volume(int(main_net))} | "
                        f"{AIService._format_volume(int(flow['super_in']))} | "
                        f"{AIService._format_volume(int(flow['big_in']))} | "
                        f"{AIService._format_volume(int(flow['mid_in']))} | "
                        f"{AIService._format_volume(int(flow['small_in']))} |"
                    )
        
        # 8. 分析要求
        prompt_parts.append(f"\n### 分析要求\n")
        prompt_parts.append("请重点分析：")
        prompt_parts.append("1. 价量配合关系")
        prompt_parts.append("2. 成交量异动情况")
        prompt_parts.append("3. 资金流向分析")
        prompt_parts.append("4. 均线系统分析")
        prompt_parts.append("5. 估值分析")
        prompt_parts.append("6. 结合大盘环境判断")
        prompt_parts.append("7. 短期趋势判断")
        prompt_parts.append("8. 操作建议")
        
        return "\n".join(prompt_parts)
