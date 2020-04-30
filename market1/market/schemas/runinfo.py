import datetime
from typing import Dict, List, Optional, Tuple, Union

from fastapi import Query

from market.const import TaskType
from market.schemas.base import BaseSearch, CommonOut, CustomBaseModel


class PortfolioRatio(CustomBaseModel):
    name: Optional[str]
    sim_task_id: Optional[str]
    start_cash: Optional[float]
    net_value: Optional[float]
    positions_value: Optional[float]
    hold_ratio: float
    pos_cnt: int
    start_dt: datetime.datetime


class QueryRunInfo(BaseSearch):
    """取收益曲线时，不适用系统配置的限制分页大小"""
    offset: int = Query(default=0, ge=0)
    count: int = Query(default=10000, gt=0, le=100000)
    task_id: str
    task_type: TaskType


class ReturnCurveInfo(CustomBaseModel):
    day: int
    returns: float
    bench_returns: float


class OrderInfo(CustomBaseModel):
    day: int
    symbol: str
    limit_price: Union[float, str]
    volume: float
    filled_volume: float
    trade_vwap: Union[float, str]
    open_vwap: Union[float, str]
    create_ts: float
    update_ts: float
    side: int
    action: int
    style: Dict
    # { style : 1, props : { trade_type : 0, limit_price : 0 } },
    status: int
    fee: float
    pnl: float
    trade_amount: float
    current: Union[float, str]


class PositionInfo(CustomBaseModel):
    day: int
    symbol: str
    multiplier: float
    side: int
    volume: float
    open_vwap: Union[float, str]  # for hide
    hold_vwap: Union[float, str]  # for hide
    market_value: Union[float, str]  # for hide
    close_price: Union[float, str]  # for hide
    sum_pnl: Optional[float]
    today_pnl: Optional[float]
    create_ts: Optional[float]
    update_ts: Optional[float]
    pos_ratio: Optional[float]


class Indicators(CustomBaseModel):
    day: Optional[int]
    cum_returns: Optional[float]
    annual_returns: Optional[float]
    retruns1m: Optional[float]
    retruns1m_bench: Optional[float]
    cum_bench_returns: Optional[float]
    annual_bench_returns: Optional[float]
    alpha: Optional[float]
    beta: Optional[float]
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    max_drawdown_period: Optional[
        Union[Tuple[datetime.datetime, datetime.datetime], List]
    ]
    daily_win_raito: Optional[float]
    win_ratio: Optional[float]
    pnl_ratio: Optional[float]


class PositionPage(CommonOut):
    data: List[PositionInfo]


class OrderPage(CommonOut):
    data: List[OrderInfo]


class CurvePage(CommonOut):
    data: List[ReturnCurveInfo]
