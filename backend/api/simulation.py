"""
实盘模拟 API

提供模拟交易会话管理、交易执行、AI 分析等端点
"""

import re
import json
from fastapi import APIRouter
from typing import Optional

from schemas.simulation import (
    SimulationCreateRequest,
    SimulationTradeRequest,
    SimulationAnalyzeRequest
)
from services.ai_service import AIService

router = APIRouter(prefix="/simulation", tags=["实盘模拟"])

# 依赖注入
monitor = None
simulation_manager = None


def set_dependencies(m, s):
    """注入依赖"""
    global monitor, simulation_manager
    monitor = m
    simulation_manager = s


@router.post("/create")
def create_simulation(req: SimulationCreateRequest):
    """创建模拟会话"""
    if req.total_days < 7 or req.total_days > 50:
        return {"status": "error", "message": "模拟天数需在7-50之间"}
    
    kline_result = monitor.get_kline_data(req.stock_code, "day", req.total_days + 30)
    kline_data = kline_result.get("data", [])
    
    if len(kline_data) < req.total_days + 1:
        return {"status": "error", "message": f"历史数据不足"}
    
    return simulation_manager.create_session(
        stock_code=req.stock_code,
        stock_name=req.stock_name,
        total_days=req.total_days,
        initial_capital=req.initial_capital,
        kline_data=kline_data
    )


@router.get("/sessions")
def get_simulation_sessions(stock_code: Optional[str] = None, status: Optional[str] = None, limit: int = 50):
    """获取模拟会话列表"""
    return simulation_manager.get_sessions(stock_code, status, limit)


@router.get("/{session_id}")
def get_simulation_session(session_id: str):
    """获取模拟会话详情"""
    return simulation_manager.get_session(session_id)


@router.get("/{session_id}/kline")
def get_simulation_kline(session_id: str):
    """获取模拟会话的K线数据"""
    session_result = simulation_manager.get_session(session_id)
    if session_result.get("status") != "success":
        return session_result
    
    session = session_result["session"]
    kline_result = monitor.get_kline_data(session["stock_code"], "day", session["total_days"] + 30)
    kline_data = kline_result.get("data", [])
    
    if not kline_data:
        return {"status": "error", "message": "无法获取K线数据"}
    
    start_idx = session.get("kline_start_idx", 0)
    visible_end = start_idx + session["current_day"] + 1
    visible_kline = kline_data[max(0, start_idx - 30):visible_end]
    current_day_data = kline_data[visible_end - 1] if visible_end <= len(kline_data) else None
    
    return {
        "status": "success",
        "kline": visible_kline,
        "current_day": current_day_data,
        "session": session
    }


@router.get("/{session_id}/minute/{date}")
def get_simulation_minute(session_id: str, date: str):
    """获取模拟会话某一天的分时数据"""
    session_result = simulation_manager.get_session(session_id)
    if session_result.get("status") != "success":
        return session_result
    
    session = session_result["session"]
    return monitor.get_history_minute_data(session["stock_code"], date)


@router.post("/trade")
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
    
    if result.get("status") == "success":
        session = result.get("session", {})
        if session.get("status") == "completed":
            kline_result = monitor.get_kline_data(session["stock_code"], "day", session["total_days"] + 30)
            kline_data = kline_result.get("data", [])
            
            if kline_data:
                end_idx = session.get("kline_start_idx", 0) + session["total_days"]
                final_price = kline_data[end_idx]["close"] if end_idx < len(kline_data) else kline_data[-1]["close"]
                complete_result = simulation_manager.complete_session(req.session_id, final_price)
                if complete_result.get("status") == "success":
                    result["session"] = complete_result["session"]
    
    return result


@router.post("/{session_id}/pause")
def pause_simulation(session_id: str):
    """暂停模拟"""
    return simulation_manager.pause_session(session_id)


@router.post("/{session_id}/resume")
def resume_simulation(session_id: str):
    """继续模拟"""
    return simulation_manager.resume_session(session_id)


@router.post("/{session_id}/abandon")
def abandon_simulation(session_id: str):
    """放弃模拟"""
    return simulation_manager.abandon_session(session_id)


@router.delete("/{session_id}")
def delete_simulation(session_id: str):
    """删除模拟记录"""
    return simulation_manager.delete_session(session_id)


@router.post("/analyze")
def analyze_simulation(req: SimulationAnalyzeRequest):
    """AI 分析模拟结果"""
    session_result = simulation_manager.get_session(req.session_id)
    if session_result.get("status") != "success":
        return session_result
    
    session = session_result["session"]
    kline_result = monitor.get_kline_data(session["stock_code"], "day", session["total_days"] + 30)
    kline_data = kline_result.get("data", [])
    
    end_idx = session.get("kline_start_idx", 0) + session["total_days"]
    final_price = kline_data[end_idx]["close"] if end_idx < len(kline_data) else kline_data[-1]["close"]
    
    result = simulation_manager.calculate_result(session, final_price)
    prompt = simulation_manager.format_for_ai_analysis(session, kline_data, result)
    
    try:
        llm_response = AIService.call_llm(req.provider, req.api_key, req.model, prompt, req.proxy, max_retries=2)
        
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', llm_response)
        if json_match:
            ai_result = json.loads(json_match.group(1))
        else:
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
