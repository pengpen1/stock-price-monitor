"""
AI 分析 API

提供 AI 模型列表获取、股票分析等端点
"""

from fastapi import APIRouter
from datetime import datetime, timedelta

from schemas.ai import AnalyzeRequest, ModelsRequest
from services.ai_service import AIService
from providers import get_provider_list

router = APIRouter(tags=["AI 分析"])

# 依赖注入
monitor = None
records_manager = None


def set_dependencies(m, r):
    """注入依赖"""
    global monitor, records_manager
    monitor = m
    records_manager = r


@router.get("/ai/providers")
def get_ai_providers():
    """获取支持的 AI 提供商列表"""
    return {"status": "success", "providers": get_provider_list()}


@router.post("/ai/models")
def get_ai_models(req: ModelsRequest):
    """获取指定提供商的可用模型列表"""
    try:
        models = AIService.get_models(req.provider, req.api_key, req.proxy)
        return {"status": "success", "models": models}
    except Exception as e:
        return {"status": "error", "message": str(e), "models": []}


@router.post("/analyze")
def analyze_stock(req: AnalyzeRequest):
    """AI 分析股票"""
    # 获取股票数据
    stock_detail = monitor.get_stock_detail(req.code)
    basic = stock_detail.get("basic", {})
    
    if not basic:
        return {"status": "error", "message": "无法获取股票基本信息"}
    
    # 获取历史记录
    trade_history = []
    ai_history = []
    
    # 获取资金流向数据
    money_flow = monitor.get_money_flow(req.code).get("data", [])
    
    # 根据分析类型获取不同范围的数据
    extra_data = None
    dragon_tiger = None
    
    if req.type == "fast":
        minute = monitor.get_minute_data(req.code).get("data", [])
        kline = monitor.get_kline_data(req.code, "day", 120).get("data", [])
        market_data = {
            "index": monitor.index_data,
            "stats": monitor.market_stats,
            "days": 1
        }
        money_flow_days = 2
    else:
        minute = monitor.get_minute_data(req.code).get("data", [])
        kline = monitor.get_kline_data(req.code, "day", 240).get("data", [])
        stats_history = monitor.get_market_stats_history(3).get("data", [])
        market_data = {
            "index": monitor.index_data,
            "stats": monitor.market_stats,
            "stats_history": stats_history,
            "days": 3
        }
        trade_history = records_manager.get_trade_records_for_analysis(req.code, 10)
        ai_history = records_manager.get_ai_records_for_analysis(req.code, 5)
        money_flow_days = 3
        extra_data = monitor.get_stock_extra_data(req.code).get("data", {})
        dragon_tiger = monitor.get_dragon_tiger(req.code).get("data", [])
    
    # 格式化提示词
    prompt = AIService.format_data_for_prompt(
        basic, minute, kline, req.inputs, market_data,
        trade_history, ai_history, money_flow, money_flow_days,
        extra_data, dragon_tiger
    )
    
    # 精准分析时计算未来5个交易日日期
    future_dates = []
    current_price = 0
    is_precise = req.type == "precise"
    
    if is_precise:
        current_price = float(basic.get("price", 0))
        today = datetime.now()
        count = 0
        day = today
        while count < 5:
            day = day + timedelta(days=1)
            if day.weekday() < 5:
                future_dates.append(day.strftime("%Y-%m-%d"))
                count += 1
    
    # 调用 LLM
    llm_result = AIService.call_llm_with_signal(
        req.provider, req.api_key, req.model, prompt, req.proxy,
        max_retries=3,
        is_precise=is_precise,
        current_price=current_price,
        future_dates=future_dates
    )
    
    result = llm_result["result"]
    signal = llm_result["signal"]
    summary = llm_result["summary"]
    prediction = llm_result.get("prediction", [])
    
    # 自动保存 AI 分析记录
    if not result.startswith("分析失败"):
        records_manager.add_ai_record(
            stock_code=req.code,
            signal=signal,
            summary=summary,
            full_result=result,
            analysis_type=req.type,
            model=req.model or req.provider
        )
    
    return {
        "status": "success",
        "result": result,
        "prompt": prompt,
        "signal": signal,
        "summary": summary,
        "prediction": prediction,
        "current_price": current_price
    }
