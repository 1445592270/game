# import datetime
import logging

from fastapi import APIRouter
from starlette.requests import Request

from market.api.share.run_info import (
    get_curves,
    get_indicators,
    get_orders,
    get_portfolio_info,
    get_positions,
)
from market.api.share.strategy import check_task_permission
from market.schemas.runinfo import CurvePage, OrderPage, PositionPage, QueryRunInfo

from market.schemas.runinfo import Indicators  # OrderInfo,; PositionInfo,

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/runinfo/orders", response_model=OrderPage, tags=["用户端——策略运行信息"])
async def query_orders(query_in: QueryRunInfo, request: Request):
    """根据名字和类型查询标签或者风格"""
    total_cnt, orders = await get_orders(
        query_in.task_type, query_in.task_id, skip=query_in.offset, limit=query_in.count
    )
    if not await check_task_permission(query_in.task_type, query_in.task_id, request):
        # current_day = int(datetime.date.today().strftime("%Y%m%d"))
        for order in orders:
            # 只隐藏最近七天的数据
            # if current_day - order["day"] > 7:
            #     break
            order["symbol"] = "****"
            order["current"] = "****"
            order["limit_price"] = "****"
            order["trade_vwap"] = "****"
            order["open_vwap"] = "****"
            try:
                order["style"]["limit_price"] = "****"
            except Exception:
                pass
    return OrderPage(total=total_cnt, data=orders)


@router.post("/runinfo/positions", response_model=PositionPage, tags=["用户端——策略运行信息"])
async def query_positions(query_in: QueryRunInfo, request: Request):
    """根据名字和类型查询标签或者风格"""
    total_cnt, positions = await get_positions(
        query_in.task_type, query_in.task_id, skip=query_in.offset, limit=query_in.count
    )
    portfolio_info = await get_portfolio_info(query_in.task_type, query_in.task_id)
    net_value = float(portfolio_info.get("net_value", 0.0))
    if not await check_task_permission(query_in.task_type, query_in.task_id, request):
        # current_day = int(datetime.date.today().strftime("%Y%m%d"))
        for pos in positions:
            # 只隐藏最近七天的数据
            # if current_day - pos["day"] > 7:
            #     break
            pos["pos_ratio"] = (
                float(pos["market_value"]) / net_value if net_value else 0.0
            )
            pos["symbol"] = "****"
            pos["open_vwap"] = "****"
            pos["hold_vwap"] = "****"
            pos["market_value"] = "****"
            pos["close_price"] = "****"
    return PositionPage(total=total_cnt, data=positions)


@router.post("/runinfo/indicators", response_model=Indicators, tags=["用户端——策略运行信息"])
async def query_indicators(query_in: QueryRunInfo):
    """根据名字和类型查询标签或者风格"""
    indicators = await get_indicators(query_in.task_type, query_in.task_id)
    return indicators


@router.post("/runinfo/curves", response_model=CurvePage, tags=["用户端——策略运行信息"])
async def query_curves(query_in: QueryRunInfo):
    """根据名字和类型查询标签或者风格"""
    total_cnt, curves = await get_curves(
        query_in.task_type, query_in.task_id, skip=query_in.offset, limit=query_in.count
    )
    return CurvePage(total=total_cnt, data=curves)
