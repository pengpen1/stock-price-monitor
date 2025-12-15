from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from monitor import StockMonitor, get_data_dir
import uvicorn
import threading
from ai_service import AIService
from records import RecordsManager
from pydantic import BaseModel
from typing import Optional, Dict, List

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    monitor_thread = threading.Thread(target=monitor.start, daemon=True)
    monitor_thread.start()
    yield
    # Shutdown
    monitor.stop()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

monitor = StockMonitor()
records_manager = RecordsManager(get_data_dir())

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Stock Price Monitor Backend Running"}

@app.get("/stocks")
def get_stocks():
    return monitor.get_stocks()

@app.post("/stocks/{code}")
def add_stock(code: str):
    return monitor.add_stock(code)

@app.delete("/stocks/{code}")
def remove_stock(code: str):
    return monitor.remove_stock(code)

# 设置相关 API
@app.get("/settings")
def get_settings():
    return monitor.get_settings()

@app.post("/settings")
def update_settings(settings: dict):
    return monitor.update_settings(settings)

# 股票排序 API
@app.post("/stocks/reorder")
def reorder_stocks(data: dict):
    return monitor.reorder_stocks(data.get("stocks", []))

# 设置重点关注
@app.post("/stocks/focus/{code}")
def set_focused_stock(code: str):
    return monitor.set_focused_stock(code)

# 股票分组 API
@app.post("/stocks/group/{code}")
def set_stock_group(code: str, data: dict):
    return monitor.set_stock_group(code, data.get("group", ""))

@app.get("/groups")
def get_groups():
    return monitor.get_groups()

@app.post("/groups")
def add_group(data: dict):
    return monitor.add_group(data.get("group", ""))

@app.delete("/groups/{group}")
def delete_group(group: str, delete_stocks: bool = False):
    return monitor.delete_group(group, delete_stocks)

# 预警相关 API
@app.post("/alerts/{code}")
def set_alert(code: str, alert_config: dict):
    return monitor.set_alert(code, alert_config)

@app.delete("/alerts/{code}")
def remove_alert(code: str):
    return monitor.remove_alert(code)

@app.get("/alerts/triggered")
def get_triggered_alerts():
    return monitor.get_triggered_alerts()

# 股票详情数据 API
@app.get("/stock/{code}/detail")
def get_stock_detail(code: str):
    return monitor.get_stock_detail(code)

@app.get("/stock/{code}/minute")
def get_minute_data(code: str):
    return monitor.get_minute_data(code)

@app.get("/stock/{code}/kline")
def get_kline_data(code: str, period: str = "day", count: int = 120):
    return monitor.get_kline_data(code, period, count)

@app.get("/stock/{code}/money-flow")
def get_money_flow(code: str):
    return monitor.get_money_flow(code)

# 大盘指数详情 API
@app.get("/index/{code}/detail")
def get_index_detail(code: str):
    return monitor.get_index_detail(code)

@app.get("/market/stats")
def get_market_stats():
    return monitor.get_market_stats()

@app.get("/market/stats/history")
def get_market_stats_history(days: int = 30):
    return monitor.get_market_stats_history(days)

class AnalyzeRequest(BaseModel):
    code: str
    type: str  # fast | precise
    provider: str
    api_key: str
    model: str
    proxy: Optional[str] = None  # 代理地址，如 http://127.0.0.1:7890
    inputs: Optional[Dict] = {}

class ImportDataRequest(BaseModel):
    stocks: Optional[Dict] = None  # stocks.json 内容
    settings: Optional[Dict] = None  # settings.json 内容
    alerts: Optional[Dict] = None  # alerts.json 内容

class ModelsRequest(BaseModel):
    provider: str
    api_key: str
    proxy: Optional[str] = None

@app.post("/ai/models")
def get_ai_models(req: ModelsRequest):
    """获取指定提供商的可用模型列表"""
    try:
        models = AIService.get_models(req.provider, req.api_key, req.proxy)
        return {"status": "success", "models": models}
    except Exception as e:
        return {"status": "error", "message": str(e), "models": []}

@app.post("/analyze")
def analyze_stock(req: AnalyzeRequest):
    # 获取股票数据
    stock_detail = monitor.get_stock_detail(req.code)
    basic = stock_detail.get("basic", {})
    
    if not basic:
        return {"status": "error", "message": "无法获取股票基本信息"}
    
    # 获取历史记录用于精准分析
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
        # 快速分析：当天大盘数据 + 最近2天资金流向
        market_data = {
            "index": monitor.index_data,
            "stats": monitor.market_stats,
            "days": 1
        }
        # 资金流向取最近2天
        money_flow_days = 2
    else:
        minute = monitor.get_minute_data(req.code).get("data", []) 
        kline = monitor.get_kline_data(req.code, "day", 240).get("data", [])
        # 精准分析：最近3天大盘数据 + 历史记录 + 最近3天资金流向
        stats_history = monitor.get_market_stats_history(3).get("data", [])
        market_data = {
            "index": monitor.index_data,
            "stats": monitor.market_stats,
            "stats_history": stats_history,
            "days": 3
        }
        # 获取交易记录和 AI 分析历史
        trade_history = records_manager.get_trade_records_for_analysis(req.code, 10)
        ai_history = records_manager.get_ai_records_for_analysis(req.code, 5)
        # 资金流向取最近3天
        money_flow_days = 3
        # 获取额外数据（换手率、量比、均线、市盈率等）
        extra_data = monitor.get_stock_extra_data(req.code).get("data", {})
        # 获取龙虎榜数据
        dragon_tiger = monitor.get_dragon_tiger(req.code).get("data", [])
        
    # 格式化提示词（包含大盘数据、历史记录和资金流向）
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
        from datetime import datetime, timedelta
        current_price = float(basic.get("price", 0))
        # 计算未来5个交易日（简单处理，跳过周末）
        today = datetime.now()
        count = 0
        day = today
        while count < 5:
            day = day + timedelta(days=1)
            # 跳过周末
            if day.weekday() < 5:  # 0-4 是周一到周五
                future_dates.append(day.strftime("%Y-%m-%d"))
                count += 1
    
    # 调用 LLM 并获取结构化结果
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
    
    # 自动保存 AI 分析记录（仅在分析成功时）
    if not result.startswith("分析失败"):
        records_manager.add_ai_record(
            stock_code=req.code,
            signal=signal,
            summary=summary,
            full_result=result,
            analysis_type=req.type,
            model=req.model or req.provider
        )
    
    # 返回结果
    return {
        "status": "success", 
        "result": result, 
        "prompt": prompt,
        "signal": signal,
        "summary": summary,
        "prediction": prediction,
        "current_price": current_price
    }

# 导出配置数据
@app.get("/data/export")
def export_data():
    """导出所有配置数据（股票列表、设置、预警）"""
    return monitor.export_data()

# 导入配置数据
@app.post("/data/import")
def import_data(req: ImportDataRequest):
    """导入配置数据"""
    return monitor.import_data(req.stocks, req.settings, req.alerts)

# 获取数据存储路径
@app.get("/data/path")
def get_data_path():
    """获取当前数据存储路径"""
    return monitor.get_data_path()

# 设置数据存储路径
@app.post("/data/path")
def set_data_path(data: dict):
    """设置自定义数据存储路径"""
    return monitor.set_data_path(data.get("path", ""))

# ========== 交易记录 API ==========

class TradeRecordRequest(BaseModel):
    stock_code: str
    type: str  # B/S/T
    price: float
    quantity: int
    reason: str
    trade_time: Optional[str] = None

class TradeRecordUpdateRequest(BaseModel):
    type: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    reason: Optional[str] = None
    trade_time: Optional[str] = None

@app.post("/records/trade")
def add_trade_record(req: TradeRecordRequest):
    """添加交易记录"""
    return records_manager.add_trade_record(
        stock_code=req.stock_code,
        trade_type=req.type,
        price=req.price,
        quantity=req.quantity,
        reason=req.reason,
        trade_time=req.trade_time
    )

@app.put("/records/trade/{record_id}")
def update_trade_record(record_id: str, req: TradeRecordUpdateRequest):
    """更新交易记录"""
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    return records_manager.update_trade_record(record_id, updates)

@app.delete("/records/trade/{record_id}")
def delete_trade_record(record_id: str):
    """删除交易记录"""
    return records_manager.delete_trade_record(record_id)

@app.get("/records/trade")
def get_trade_records(stock_code: Optional[str] = None, limit: int = 100):
    """获取交易记录"""
    return records_manager.get_trade_records(stock_code, limit)

@app.get("/records/trade/{stock_code}")
def get_stock_trade_records(stock_code: str, limit: int = 100):
    """获取指定股票的交易记录"""
    return records_manager.get_trade_records(stock_code, limit)

# ========== AI 分析记录 API ==========

@app.get("/records/ai")
def get_ai_records(stock_code: Optional[str] = None, limit: int = 50):
    """获取 AI 分析记录"""
    return records_manager.get_ai_records(stock_code, limit)

@app.get("/records/ai/{stock_code}")
def get_stock_ai_records(stock_code: str, limit: int = 50):
    """获取指定股票的 AI 分析记录"""
    return records_manager.get_ai_records(stock_code, limit)

# ========== 持仓计算 API ==========

@app.get("/records/position/{stock_code}")
def get_position(stock_code: str):
    """根据交易记录计算持仓成本和数量"""
    return records_manager.calculate_position(stock_code)

# ========== 股票额外数据 API ==========

@app.get("/stock/{code}/extra")
def get_stock_extra(code: str):
    """获取股票额外数据（换手率、量比、均线、市盈率等）"""
    return monitor.get_stock_extra_data(code)

@app.get("/stock/{code}/dragon-tiger")
def get_dragon_tiger(code: str):
    """获取龙虎榜数据"""
    return monitor.get_dragon_tiger(code)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
