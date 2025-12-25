"""
健康检查 API

提供服务健康状态检查端点
"""

from fastapi import APIRouter

router = APIRouter(tags=["健康检查"])


@router.get("/")
def read_root():
    """健康检查"""
    return {"status": "ok", "message": "Stock Price Monitor Backend Running"}
