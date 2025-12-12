from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from monitor import StockMonitor
import uvicorn
import threading
from ai_service import AIService
from pydantic import BaseModel
from typing import Optional, Dict

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
        
    # 根据分析类型获取不同范围的数据
    if req.type == "fast":
        minute = monitor.get_minute_data(req.code).get("data", [])
        kline = monitor.get_kline_data(req.code, "day", 120).get("data", [])
        # 快速分析：当天大盘数据
        market_data = {
            "index": monitor.index_data,
            "stats": monitor.market_stats,
            "days": 1
        }
    else:
        minute = monitor.get_minute_data(req.code).get("data", []) 
        kline = monitor.get_kline_data(req.code, "day", 240).get("data", [])
        # 精准分析：最近3天大盘数据
        stats_history = monitor.get_market_stats_history(3).get("data", [])
        market_data = {
            "index": monitor.index_data,
            "stats": monitor.market_stats,
            "stats_history": stats_history,
            "days": 3
        }
        
    # 格式化提示词（包含大盘数据）
    prompt = AIService.format_data_for_prompt(basic, minute, kline, req.inputs, market_data)
    
    # 调用 LLM（支持代理）
    result = AIService.call_llm(req.provider, req.api_key, req.model, prompt, req.proxy)
    
    # 返回结果和 prompt（用于前端展示）
    return {"status": "success", "result": result, "prompt": prompt}

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

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
