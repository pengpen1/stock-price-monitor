from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from monitor import StockMonitor, get_data_dir
import uvicorn
import threading
from ai_service import AIService
from records import RecordsManager
from simulation import SimulationManager
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
simulation_manager = SimulationManager(get_data_dir())

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
    stock_name: Optional[str] = None
    type: str  # B/S/T
    price: float
    quantity: int
    reason: str
    trade_time: Optional[str] = None
    mood: Optional[str] = "calm"  # calm/anxious/panic/fear/excited
    level: Optional[int] = 2  # 1/2/3

class TradeRecordUpdateRequest(BaseModel):
    type: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    reason: Optional[str] = None
    trade_time: Optional[str] = None
    mood: Optional[str] = None
    level: Optional[int] = None
    stock_name: Optional[str] = None

@app.post("/records/trade")
def add_trade_record(req: TradeRecordRequest):
    """添加交易记录"""
    return records_manager.add_trade_record(
        stock_code=req.stock_code,
        trade_type=req.type,
        price=req.price,
        quantity=req.quantity,
        reason=req.reason,
        trade_time=req.trade_time,
        mood=req.mood,
        level=req.level,
        stock_name=req.stock_name
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

# ========== 交易风格分析 API ==========

@app.get("/records/analysis")
def get_trade_style_analysis(stock_code: Optional[str] = None):
    """获取交易风格分析"""
    return records_manager.get_trade_style_analysis(stock_code)

@app.get("/records/stocks")
def get_trade_stock_codes():
    """获取所有有交易记录的股票代码"""
    codes = records_manager.get_all_stock_codes()
    return {"status": "success", "codes": codes}

@app.get("/records/export/md")
def export_trade_records_md(stock_code: Optional[str] = None):
    """导出交易记录为 Markdown 格式"""
    md_content = records_manager.export_to_markdown(stock_code)
    return {"status": "success", "content": md_content}

class ImportMdRequest(BaseModel):
    content: str

@app.post("/records/import/md")
def import_trade_records_md(req: ImportMdRequest):
    """从 Markdown 格式导入交易记录"""
    return records_manager.import_from_markdown(req.content)

# ========== 股票额外数据 API ==========

@app.get("/stock/{code}/extra")
def get_stock_extra(code: str):
    """获取股票额外数据（换手率、量比、均线、市盈率等）"""
    return monitor.get_stock_extra_data(code)

@app.get("/stock/{code}/dragon-tiger")
def get_dragon_tiger(code: str):
    """获取龙虎榜数据"""
    return monitor.get_dragon_tiger(code)

# ========== 实盘模拟 API ==========

class SimulationCreateRequest(BaseModel):
    stock_code: str
    stock_name: str
    total_days: int  # 7-50
    initial_capital: float = 1000000  # 默认100万

class SimulationTradeRequest(BaseModel):
    session_id: str
    trade_type: str  # buy/sell/skip
    price: float = 0
    quantity: int = 0
    reason: str = ""
    current_date: str = ""

class SimulationAnalyzeRequest(BaseModel):
    session_id: str
    provider: str
    api_key: str
    model: str
    proxy: Optional[str] = None

@app.post("/simulation/create")
def create_simulation(req: SimulationCreateRequest):
    """创建模拟会话"""
    # 验证天数范围
    if req.total_days < 7 or req.total_days > 50:
        return {"status": "error", "message": "模拟天数需在7-50之间"}
    
    # 获取足够的K线数据
    kline_result = monitor.get_kline_data(req.stock_code, "day", req.total_days + 30)
    kline_data = kline_result.get("data", [])
    
    if len(kline_data) < req.total_days + 1:
        return {"status": "error", "message": f"历史数据不足，需要至少 {req.total_days + 1} 天"}
    
    return simulation_manager.create_session(
        stock_code=req.stock_code,
        stock_name=req.stock_name,
        total_days=req.total_days,
        initial_capital=req.initial_capital,
        kline_data=kline_data
    )

@app.get("/simulation/sessions")
def get_simulation_sessions(stock_code: Optional[str] = None, status: Optional[str] = None, limit: int = 50):
    """获取模拟会话列表"""
    return simulation_manager.get_sessions(stock_code, status, limit)

@app.get("/simulation/{session_id}")
def get_simulation_session(session_id: str):
    """获取模拟会话详情"""
    return simulation_manager.get_session(session_id)

@app.get("/simulation/{session_id}/kline")
def get_simulation_kline(session_id: str):
    """获取模拟会话的K线数据（只返回到当前日期）"""
    session_result = simulation_manager.get_session(session_id)
    if session_result.get("status") != "success":
        return session_result
    
    session = session_result["session"]
    # 获取完整K线数据
    kline_result = monitor.get_kline_data(session["stock_code"], "day", session["total_days"] + 30)
    kline_data = kline_result.get("data", [])
    
    if not kline_data:
        return {"status": "error", "message": "无法获取K线数据"}
    
    # 计算可见范围：从起始索引到当前天数
    start_idx = session.get("kline_start_idx", 0)
    visible_end = start_idx + session["current_day"] + 1  # +1 显示当天
    
    # 返回可见的K线数据
    visible_kline = kline_data[max(0, start_idx - 30):visible_end]  # 多返回30天历史用于均线计算
    
    # 当前交易日数据
    current_day_data = kline_data[visible_end - 1] if visible_end <= len(kline_data) else None
    
    return {
        "status": "success",
        "kline": visible_kline,
        "current_day": current_day_data,
        "session": session
    }

@app.get("/simulation/{session_id}/minute/{date}")
def get_simulation_minute(session_id: str, date: str):
    """获取模拟会话某一天的分时数据（历史分时）"""
    session_result = simulation_manager.get_session(session_id)
    if session_result.get("status") != "success":
        return session_result
    
    session = session_result["session"]
    # 获取历史分时数据
    minute_data = monitor.get_history_minute_data(session["stock_code"], date)
    return minute_data

@app.post("/simulation/trade")
def execute_simulation_trade(req: SimulationTradeRequest):
    """执行模拟交易"""
    result = simulation_manager.execute_trade(
        session_id=req.session_id,
        trade_type=req.trade_type,
        price=req.price,
        quantity=req.quantity,
        reason=req.reason,
        current_date=req.current_date
    )
    
    # 如果模拟完成，自动清仓并计算最终收益
    if result.get("status") == "success":
        session = result.get("session", {})
        if session.get("status") == "completed":
            # 获取最终价格（下一天的收盘价）
            kline_result = monitor.get_kline_data(session["stock_code"], "day", session["total_days"] + 30)
            kline_data = kline_result.get("data", [])
            
            if kline_data:
                end_idx = session.get("kline_start_idx", 0) + session["total_days"]
                final_price = kline_data[end_idx]["close"] if end_idx < len(kline_data) else kline_data[-1]["close"]
                
                # 完成会话（自动清仓）
                complete_result = simulation_manager.complete_session(req.session_id, final_price)
                if complete_result.get("status") == "success":
                    result["session"] = complete_result["session"]
    
    return result

@app.post("/simulation/{session_id}/pause")
def pause_simulation(session_id: str):
    """暂停模拟"""
    return simulation_manager.pause_session(session_id)

@app.post("/simulation/{session_id}/resume")
def resume_simulation(session_id: str):
    """继续模拟"""
    return simulation_manager.resume_session(session_id)

@app.post("/simulation/{session_id}/abandon")
def abandon_simulation(session_id: str):
    """放弃模拟"""
    return simulation_manager.abandon_session(session_id)

@app.delete("/simulation/{session_id}")
def delete_simulation(session_id: str):
    """删除模拟记录"""
    return simulation_manager.delete_session(session_id)

@app.post("/simulation/analyze")
def analyze_simulation(req: SimulationAnalyzeRequest):
    """AI分析模拟结果"""
    session_result = simulation_manager.get_session(req.session_id)
    if session_result.get("status") != "success":
        return session_result
    
    session = session_result["session"]
    
    # 获取K线数据
    kline_result = monitor.get_kline_data(session["stock_code"], "day", session["total_days"] + 30)
    kline_data = kline_result.get("data", [])
    
    # 计算最终价格（模拟结束后一天的收盘价）
    end_idx = session.get("kline_start_idx", 0) + session["total_days"]
    final_price = kline_data[end_idx]["close"] if end_idx < len(kline_data) else kline_data[-1]["close"]
    
    # 计算结果
    result = simulation_manager.calculate_result(session, final_price)
    
    # 格式化AI分析提示词
    prompt = simulation_manager.format_for_ai_analysis(session, kline_data, result)
    
    # 调用AI分析
    try:
        from ai_service import AIService
        llm_response = AIService.call_llm(req.provider, req.api_key, req.model, prompt, req.proxy, max_retries=2)
        
        # 解析JSON结果
        import re
        import json
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', llm_response)
        if json_match:
            ai_result = json.loads(json_match.group(1))
        else:
            # 尝试直接解析
            json_match = re.search(r'\{[\s\S]*\}', llm_response)
            if json_match:
                ai_result = json.loads(json_match.group())
            else:
                ai_result = {
                    "score": 60,
                    "grade": "C",
                    "strengths": [],
                    "weaknesses": [],
                    "suggestions": [],
                    "analysis": llm_response
                }
        
        return {
            "status": "success",
            "result": result,
            "ai_result": ai_result,
            "session": session
        }
    except Exception as e:
        return {
            "status": "success",
            "result": result,
            "ai_result": None,
            "error": str(e),
            "session": session
        }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
