"""
股票监控系统后端主入口

本文件只负责应用装配：
1. 初始化 FastAPI 应用和中间件
2. 创建各模块实例
3. 注入依赖
4. 注册所有 API 路由
5. 启动后台监控线程

架构说明：
- api/: API 路由层（类似前端 views）
- schemas/: 数据模型定义（类似前端 types）
- services/: 业务服务层（类似前端 components）
- providers/: AI 模型提供商（基础设施层）
- repositories/: 数据存储层
- core/: 核心配置和工具
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading
import uvicorn

# 导入核心模块（从 domain 层）
from domain import StockMonitor, RecordsManager, SimulationManager, NotesManager
from core.config import get_data_dir

# 导入 API 路由
from api import (
    health_router,
    stocks_router,
    stock_detail_router,
    settings_router,
    alerts_router,
    market_router,
    ai_router,
    records_router,
    simulation_router,
    notes_router,
    data_router,
)

# 导入依赖注入函数
from api import stocks as stocks_api
from api import stock_detail as stock_detail_api
from api import settings as settings_api
from api import alerts as alerts_api
from api import market as market_api
from api import ai as ai_api
from api import records as records_api
from api import simulation as simulation_api
from api import notes as notes_api
from api import data as data_api


# ========== 创建实例 ==========
monitor = StockMonitor()
records_manager = RecordsManager(get_data_dir())
notes_manager = NotesManager(get_data_dir())
simulation_manager = SimulationManager(get_data_dir())


# ========== 应用生命周期管理 ==========
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期：启动时开启监控线程，关闭时停止监控"""
    monitor_thread = threading.Thread(target=monitor.start, daemon=True)
    monitor_thread.start()
    yield
    monitor.stop()


# ========== 初始化 FastAPI 应用 ==========
app = FastAPI(
    title="股票监控系统 API",
    description="提供股票监控、AI 分析、交易记录等功能",
    version="1.2.1",
    lifespan=lifespan
)

# 配置 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== 依赖注入 ==========
stocks_api.set_monitor(monitor)
stock_detail_api.set_monitor(monitor)
settings_api.set_monitor(monitor)
alerts_api.set_monitor(monitor)
market_api.set_monitor(monitor)
data_api.set_monitor(monitor)
ai_api.set_dependencies(monitor, records_manager)
records_api.set_records_manager(records_manager)
simulation_api.set_dependencies(monitor, simulation_manager)
notes_api.set_notes_manager(notes_manager)


# ========== 注册路由 ==========
app.include_router(health_router)
app.include_router(stocks_router)
app.include_router(stock_detail_router)
app.include_router(settings_router)
app.include_router(alerts_router)
app.include_router(market_router)
app.include_router(ai_router)
app.include_router(records_router)
app.include_router(simulation_router)
app.include_router(notes_router)
app.include_router(data_router)


# ========== 启动入口 ==========
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
