import datetime
import logging
from typing import Any, Dict
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from starlette.requests import Request
from tortoise import Tortoise
from tortoise.exceptions import DoesNotExist

from market.api.share.run_info import (
    get_curves,
    get_indicators,
    get_period_returns,
    get_portfolio_info,
    get_today_positons,
    get_today_returns,
)
from market.api.share.strategy import check_task_permission, search_strategy,search_strategy1
from market.const import TaskType
from market.core.security import require_active_user
from market.models.const import ListStatus, ProductType
from market.models.order import UserOrder
from market.models.strategy import QStrategy
from market.models.package import StrategyPackage
from market.models.user import MarketUser
from market.schemas.base import CommonOut
from market.schemas.runinfo import PortfolioRatio
from market.schemas.strategy import BuyedQStrategySearch  # QStrategyInfo,
from market.schemas.strategy import (
    BuyedQStrategyInfo,
    BuyedQStrategySearchOut,
    QStrategyBasicInfo,
    QStrategySearch,
    QStrategySearchOut,
    QStrategySearchOVOut,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/strategy/check/{task_id}", response_model=CommonOut, tags=["用户端——策略运行信息"]
)
async def check_buyed(task_id: str, request: Request):
    """检查是否需要因此策略信息"""
    try:
        if await check_task_permission(TaskType.PAPER_TRADING, task_id, request):
            return CommonOut()
    except Exception:
        pass
    return CommonOut(errCode=-1, errMsg="没有权限")


@router.post("/strategy/copy/{task_id}", response_model=CommonOut, tags=["用户端——策略运行信息"])
async def get_strategy_code(task_id: str, request: Request):
    """检查是否需要因此策略信息"""
    if not await check_task_permission(TaskType.PAPER_TRADING, task_id, request):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "没有权限")
    # get code
    query_str = "SELECT backtest_id FROM wk_simulation WHERE task_id=%s"
    client = Tortoise.get_connection("qpweb")
    try:
        rows = await client.execute_query_dict(query_str, task_id)
    except TypeError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="复制错误，策略已不存在")
    if len(rows) != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="复制错误，策略已不存在")
    backtest_id = rows[0]["backtest_id"]

    query_str = f"SELECT code FROM wk_strategy_backtest WHERE id=%s"
    try:
        rows = await client.execute_query_dict(query_str, backtest_id)
    except TypeError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="复制错误，策略已不存在")
    if len(rows) != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="复制错误，策略已不存在")

    code = rows[0]["code"]
    return CommonOut(data=code)


@router.get(
    "/strategy/portfolio/{product_id}",
    response_model=PortfolioRatio,
    tags=["用户端——策略信息"],
)
async def get_portfolio(product_id: UUID):
    """获取策略仓位占比信息"""
    try:
        strategy = await QStrategy.get(product_id=product_id, status=ListStatus.online)
    except DoesNotExist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "未找到该策略")
    portfolio_info = await get_portfolio_info(TaskType.PAPER_TRADING, strategy.task_id)
    positions = await get_today_positons(TaskType.PAPER_TRADING, strategy.task_id)
    try:
        pos_ratio = round(
            float(portfolio_info["positions_value"])
            / float(portfolio_info["net_value"]),
            2,
        )
    except (ZeroDivisionError, KeyError):
        pos_ratio = 0.0
    return {
        "name": strategy.name,
        "task_id": strategy.task_id,
        "start_cash": portfolio_info.get("start_cash", 0),
        "net_value": portfolio_info.get("net_value", 0),
        "positions_value": portfolio_info.get("positions_value", 0),
        "hold_ratio": pos_ratio,
        "pos_cnt": len(positions),
        "start_dt": strategy.sim_start_dt,
    }


@router.get(
    "/strategy/show/{product_id}", response_model=QStrategyBasicInfo, tags=["用户端——策略信息"]
)
async def get_strategy_info(product_id: UUID):
    """获取策略概览信息"""
    try:
        strategy = await QStrategy.get(product_id=product_id, status=ListStatus.online)
    except DoesNotExist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "未找到该策略")
    data = {
        "product_id": strategy.product_id,
        "name": strategy.name,
        "style": strategy.style,
        "category": strategy.category,
        "tags": strategy.tags,
        "author_name": strategy.author_name,
        "ideas": strategy.ideas,
        "desc": strategy.desc,
        "buyout_price": strategy.buyout_price,
        "task_id": strategy.task_id,
        "sell_cnt": strategy.sell_cnt_show,
        "total_cnt": strategy.total_cnt,
        "sim_start_dt": strategy.sim_start_dt,
        "online_dt": strategy.online_dt,
        "period_prices": strategy.period_prices,
        "enable_discount": strategy.enable_discount,
        "discount_info": strategy.discount_info,
        "allow_coupon": strategy.allow_coupon,
    }
    indicators = await get_indicators(TaskType.PAPER_TRADING, strategy.task_id)
    data.update(indicators)
    return_info = await get_today_returns(TaskType.PAPER_TRADING, strategy.task_id)
    if return_info:
        data.update(return_info[0])
    data["unv"] = round(data.get("returns", 0) + 1, 2)
    period_returns = await get_period_returns(strategy.task_id)
    data.update(period_returns)
    return data


@router.post(
    "/strategy/list", response_model=BuyedQStrategySearchOut, tags=["用户端——策略信息"]
)
async def list_strategies(
    schema_in: BuyedQStrategySearch,
    current_user: MarketUser = Depends(require_active_user),
):
    """列出已购买策略"""
    query = await UserOrder.filter(
        user_id=current_user.id, product_type=ProductType.package
    )
    total_count = 0
    product_ids = []
    order_info_dict = {}
    for order in query:
        total_count += 1
        #print(order.product_id)
        product_ids.append(order.product_id)
        order_info_dict[order.product_id] = {
            "order_id": order.id,
            "total_cash": order.total_cash,
            "total_days": order.total_days,
            "days": order.days,
            "gift_days": order.gift_days,
            "coupon_days": order.coupon_days,
            "coupon_cash": order.coupon_cash,
            "payed_cash": order.payed_cash,
            "expire_dt": order.expire_dt,
            "create_dt": order.create_dt,
            "pay_dt": order.pay_dt,
        }
    strategy_list = await QStrategy.filter(
                    package_id__in=product_ids, status=ListStatus.online
                        )
    strategy_list1 = []
    for j in strategy_list:
        strategy_list1.append(j)
    data = []
    for strategy in strategy_list1:
        info = dict(**strategy.__dict__)
        info.update(**order_info_dict[strategy.package_id])
        data.append(BuyedQStrategyInfo(**info))
    return BuyedQStrategySearchOut(total=total_count, data=data,)


@router.post("/strategy/find", response_model=QStrategySearchOut, tags=["用户端——策略信息"])
async def user_search_strategy(schema_in: QStrategySearch):
    """搜索策略"""
    return await search_strategy(schema_in)


@router.post(
    "/strategy/find/ov", response_model=QStrategySearchOVOut, tags=["用户端——策略信息"]
)
async def strategy_overview(schema_in: QStrategySearch):
    """首页策略列表"""
    task_id = schema_in.task_id
    package_id = schema_in.package_id
    sort = schema_in.sort
    print('sort ::::: ',sort,'package_id::::: ',package_id)
    #package_id = schema_in.package_id
    if not package_id:
        #print('start')
        data = []
        info2 = []
        info1 = []
        task = []#存在cum_returns
        task2 = []
        #info: Dict[str,Any] = {'curve':[],'bench_curve':[]}
        total_cnt, strategies = await search_strategy(schema_in, return_strategy_list=True)
        for strategy in strategies:
            indicators = await get_indicators(TaskType.PAPER_TRADING, strategy.task_id)
            #print(indicators,'indicators 222222222222222222222222 这是indicators')
            #indicators = 
            _, curve = await get_curves(TaskType.PAPER_TRADING, strategy.task_id)
            #print(curve,'111111111111111111111111111111 这是curve')
            return_info = await get_today_returns(TaskType.PAPER_TRADING, strategy.task_id)
            info: Dict[str, Any] = {"curve": [], "bench_curve": []}
            for daily_curve in curve:
                info["curve"].append((daily_curve["day"], daily_curve["returns"]))
                info["bench_curve"].append(
                    (daily_curve["day"], daily_curve["bench_returns"])
                )
            #info1.append(indicators)
            #if sort == '-1':
            #    sort_cum = sorted()
            info.update(indicators)
            #print(info,'info 11111111111111122222222222222222222')
            if return_info:
                info.update(return_info[0])
            info.update(strategy.__dict__)
            data.append(info)
        for i in data:
            if 'cum_returns' not in i.keys():
                info1.append(i)
            else:
                task.append(i)
        for cash in data:
            if 'sim_start_cash' not in cash.keys():
                info2.append(cash)
            else:
                task2.append(cash)
        if sort == '1':
            sort_cum = sorted(task,key=lambda s:s['cum_returns'],reverse = False)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '-1':
            sort_cum = sorted(task,key=lambda s:s['cum_returns'],reverse = True)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '2':
            sort_cum = sorted(task,key=lambda s:s['daily_returns'],reverse=False)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '-2':
            sort_cum = sorted(task,key=lambda s:s['daily_returns'],reverse=True)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '3':
            sort_cum = sorted(task,key=lambda s:s['annual_returns'],reverse=False)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '-3':
            sort_cum = sorted(task,key=lambda s:s['annual_returns'],reverse=True)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '4':
            sort_cum = sorted(task,key=lambda s:s['max_drawdown'],reverse=False)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '-4':
            sort_cum = sorted(task,key=lambda s:s['max_drawdown'],reverse=True)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '5':
            sort_cum = sorted(task2,key=lambda s:s['sim_start_cash'],reverse=False)
            for j in info2:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '-5':
            sort_cum = sorted(task2,key=lambda s:s['sim_start_cash'],reverse=True)
            for j in info2:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        else:
            pass
        #for sort_cumm in sort_cum:
        #    info.update()
        #print(data,'data数据啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊啊')
        #return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
    else:
        #print('end')

        if schema_in.status:
            strategies = await QStrategy.filter(package_id = package_id,status=schema_in.status)
        else:
            strategies = await QStrategy.filter(package_id = package_id,status=ListStatus.online)
        if schema_in.product_id:
            query = query.filter(product_id=schema_in.product_id)
        if schema_in.market_id:
            strategies = await QStrategy.filter(market_id = schema_in.market_id)
        if schema_in.package_id:
            strategies = await QStrategy.filter(package_id = schema_in.package_id)
        if schema_in.task_id:
            strategies = await QStrategy.filter(task_id__contains = schema_in.task_id)
        if schema_in.style:
            strategies = await QStrategy.filter(style__contains = schema_in.style)
        if schema_in.category:
            strategies = await QStrategy.filter(category__contains = schema_in.category)
        if schema_in.name:
            strategies = await QStrategy.filter(name__contains = schema_in.name)
        if schema_in.package_id and schema_in.style:
            strategies = await QStrategy.filter(package_id = schema_in.package_id,style__contains = schema_in.style)
        total_cnt = 0
        data = []
        info2 = []
        info1 = []
        task = []
        task2 = []
        #print(strategies,'1111111111111111111111')
        for strategy in strategies: 
            total_cnt += 1
            indicators = await get_indicators(TaskType.PAPER_TRADING, strategy.task_id)
            _, curve = await get_curves(TaskType.PAPER_TRADING, strategy.task_id)
            return_info = await get_today_returns(TaskType.PAPER_TRADING, strategy.task_id)
            info: Dict[str, Any] = {"curve": [], "bench_curve": []}
            for daily_curve in curve:
                info["curve"].append((daily_curve["day"], daily_curve["returns"]))
                info["bench_curve"].append(
                        (daily_curve["day"], daily_curve["bench_returns"])
                        )
            info.update(indicators)
            if return_info:
                info.update(return_info[0])
            info.update(strategy.__dict__)
            data.append(info)
        for i in data:
            if 'cum_returns' not in i.keys():
                info1.append(i)
            else:
                task.append(i)
        for cash in data:
            if 'sim_start_cash' not in cash.keys():
                info2.append(cash)
            else:
                task2.append(cash)
        if sort == '1':
            sort_cum = sorted(task,key=lambda s:s['cum_returns'],reverse = False)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '-1':
            sort_cum = sorted(task,key=lambda s:s['cum_returns'],reverse = True)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '2':
            sort_cum = sorted(task,key=lambda s:s['daily_returns'],reverse=False)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '-2':
            sort_cum = sorted(task,key=lambda s:s['daily_returns'],reverse=True)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '3':
            sort_cum = sorted(task,key=lambda s:s['annual_returns'],reverse=False)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '-3':
            sort_cum = sorted(task,key=lambda s:s['annual_returns'],reverse=True)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '4':
            sort_cum = sorted(task,key=lambda s:s['max_drawdown'],reverse=False)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '-4':
            sort_cum = sorted(task,key=lambda s:s['max_drawdown'],reverse=True)
            for j in info1:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '5':
            sort_cum = sorted(task2,key=lambda s:s['sim_start_cash'],reverse=False)
            for j in info2:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        elif sort == '-5':
            sort_cum = sorted(task2,key=lambda s:s['sim_start_cash'],reverse=True)
            for j in info2:
                sort_cum.append(j)
            return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
        else:
            pass
        #return QStrategySearchOVOut(total=total_cnt, data=sort_cum)
