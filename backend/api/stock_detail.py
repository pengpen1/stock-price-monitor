"""
股票详情 API

提供单个股票的详细数据端点：
- 股票详情（基本信息、行情数据）
- 分时数据
- K线数据
- 资金流向
- 额外数据（财务指标等）
- 龙虎榜数据
"""

from fastapi import APIRouter

router = APIRouter(prefix="/stock", tags=["股票详情"])

# monitor 实例将在 main.py 中注入
monitor = None


def set_monitor(m):
    """注入 monitor 实例"""
    global monitor
    monitor = m


@router.get("/{code}/detail")
def get_stock_detail(code: str):
    """获取股票详情"""
    return monitor.get_stock_detail(code)


@router.get("/{code}/minute")
def get_minute_data(code: str):
    """获取分时数据"""
    return monitor.get_minute_data(code)


@router.get("/{code}/kline")
def get_kline_data(code: str, period: str = "day", count: int = 120):
    """获取K线数据"""
    return monitor.get_kline_data(code, period, count)


@router.get("/{code}/money-flow")
def get_money_flow(code: str):
    """获取资金流向"""
    return monitor.get_money_flow(code)


@router.get("/{code}/extra")
def get_stock_extra(code: str):
    """获取股票额外数据（财务指标等）"""
    return monitor.get_stock_extra_data(code)


@router.get("/{code}/dragon-tiger")
def get_dragon_tiger(code: str):
    """获取龙虎榜数据"""
    return monitor.get_dragon_tiger(code)
