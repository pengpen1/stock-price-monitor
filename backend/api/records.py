"""
交易记录 API

提供交易记录、AI 分析记录的增删改查等端点
"""

from fastapi import APIRouter
from typing import Optional

from schemas.records import TradeRecordRequest, TradeRecordUpdateRequest, ImportMdRequest

router = APIRouter(prefix="/records", tags=["交易记录"])

# 依赖注入
records_manager = None


def set_records_manager(r):
    """注入 records_manager 实例"""
    global records_manager
    records_manager = r


# ========== 交易记录 ==========
@router.post("/trade")
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


@router.put("/trade/{record_id}")
def update_trade_record(record_id: str, req: TradeRecordUpdateRequest):
    """更新交易记录"""
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    return records_manager.update_trade_record(record_id, updates)


@router.delete("/trade/{record_id}")
def delete_trade_record(record_id: str):
    """删除交易记录"""
    return records_manager.delete_trade_record(record_id)


@router.get("/trade")
def get_trade_records(stock_code: Optional[str] = None, limit: int = 100):
    """获取交易记录"""
    return records_manager.get_trade_records(stock_code, limit)


@router.get("/trade/{stock_code}")
def get_stock_trade_records(stock_code: str, limit: int = 100):
    """获取指定股票的交易记录"""
    return records_manager.get_trade_records(stock_code, limit)


# ========== AI 分析记录 ==========
@router.get("/ai")
def get_ai_records(stock_code: Optional[str] = None, limit: int = 50):
    """获取 AI 分析记录"""
    return records_manager.get_ai_records(stock_code, limit)


@router.get("/ai/{stock_code}")
def get_stock_ai_records(stock_code: str, limit: int = 50):
    """获取指定股票的 AI 分析记录"""
    return records_manager.get_ai_records(stock_code, limit)


# ========== 持仓和分析 ==========
@router.get("/position/{stock_code}")
def get_position(stock_code: str):
    """计算持仓"""
    return records_manager.calculate_position(stock_code)


@router.get("/analysis")
def get_trade_style_analysis(stock_code: Optional[str] = None):
    """获取交易风格分析"""
    return records_manager.get_trade_style_analysis(stock_code)


@router.get("/stocks")
def get_trade_stock_codes():
    """获取所有有交易记录的股票代码"""
    codes = records_manager.get_all_stock_codes()
    return {"status": "success", "codes": codes}


# ========== 导入导出 ==========
@router.get("/export/md")
def export_trade_records_md(stock_code: Optional[str] = None):
    """导出交易记录为 Markdown"""
    md_content = records_manager.export_to_markdown(stock_code)
    return {"status": "success", "content": md_content}


@router.post("/import/md")
def import_trade_records_md(req: ImportMdRequest):
    """从 Markdown 导入交易记录"""
    return records_manager.import_from_markdown(req.content)
