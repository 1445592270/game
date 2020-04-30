import datetime
import logging
from typing import List

from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from tortoise import Tortoise

from market.models.const import ListStatus, ProductType, ReviewOP, ReviewStatus
from market.models.market import StrategyMarket
from market.models.review import ReviewRecord
from market.models.strategy import QStrategy
from market.schemas.base import CommonOut
from market.schemas.review import (
    ApplyQuery,
    ApplyQueryOut,
    OfflineApplyInfo,
    OnlineApplyInfo,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/apply/strategy/query", response_model=ApplyQueryOut, tags=["后台——上下架申请"])
async def query_list_info(query_in: ApplyQuery):
    """查询上下架申请状态"""
    client = Tortoise.get_connection("qpweb")
    sim_ids = query_in.sim_id
    if isinstance(sim_ids, str):
        sim_ids = [sim_ids]
    # get simulation info
    query_str = f"SELECT user_id FROM wk_simulation WHERE id in ({','.join(['%s']*len(sim_ids))})"
    try:
        rows = await client.execute_query_dict(query_str, sim_ids)
    except TypeError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请检查查询参数")
    if len(rows) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请检查查询参数")
    # get user
    user_ids = [row["user_id"] for row in rows]
    if len(set(user_ids)) > 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请检查查询参数")
    user_id = str(user_ids[0])
    row = await client.execute_query_dict(
        "SELECT phone FROM wk_user WHERE id=%s", user_id
    )
    if len(row) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请检查查询参数")
    user_phone = row[0]["phone"]
    if query_in.user_id != user_phone:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请检查查询参数")

    strategy_list = await QStrategy.filter(
        status__in=[
            ListStatus.online_review,
            ListStatus.online,
            ListStatus.offline_review,
            ListStatus.online_rejected,
            ListStatus.offline_rejected,
            ListStatus.offline,
        ],
        sim_id__in=sim_ids,
    ).all()

    if not strategy_list:
        return []

    product_ids = [strategy.product_id for strategy in strategy_list]
    review_list = await ReviewRecord.filter(
        product_id__in=product_ids, product_type=ProductType.qstrategy
    ).all()
    if not review_list:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请检查查询参数")

    apply_info = {}
    for review in review_list:
        apply_info[review.product_id] = {
            "status": review.review_status,
            "review_dt": review.review_dt,
            "msg": review.review_msg,
        }

    strategy_list = await QStrategy.filter(product_id__in=product_ids)
    for strategy in strategy_list:
        if strategy.product_id not in apply_info:
            continue
        apply_info[strategy.product_id].update(
            {
                "sim_id": strategy.sim_id,
                "task_id": strategy.task_id,
                "name": strategy.name,
                "sell_cnt": strategy.sell_cnt,
                "total_cnt": strategy.total_cnt,
            }
        )
    return ApplyQueryOut(total_cnt=len(apply_info), data=list(apply_info.values()))


@router.post("/apply/strategy/list", response_model=CommonOut, tags=["后台——上下架申请"])
async def list_apply(schema_in: OnlineApplyInfo):
    """策略上架申请"""
    strategy = await QStrategy.filter(
        status__in=[
            ListStatus.online_review,
            ListStatus.online,
            ListStatus.offline_review,
        ],
        sim_id=schema_in.sim_id,
    ).get_or_none()

    if strategy:
        return CommonOut(errCode=-1, errMsg="申请失败，该策略在商城已存在")

    client = Tortoise.get_connection("qpweb")
    # get simulation info
    row = await client.execute_query_dict(
        "SELECT user_id, name, task_id, backtest_id, init_money, start_date FROM wk_simulation WHERE id=%s",
        schema_in.sim_id,
    )
    if len(row) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="未找到对应的模拟交易"
        )
    task_id = str(row[0]["task_id"])
    user_id = str(row[0]["user_id"])
    sim_name = str(row[0]["name"])
    backtest_id = row[0]["backtest_id"]
    sim_start_cash = float(row[0]["init_money"])
    sim_start_dt = datetime.datetime.combine(row[0]["start_date"], datetime.time())

    row = await client.execute_query_dict(
        "SELECT phone FROM wk_user WHERE id=%s", user_id
    )
    if len(row) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="模拟交易的用户信息不一致！！！"
        )
    user_phone = row[0]["phone"]
    if user_phone != schema_in.user_id:
        logger.error(
            "request list apply for %s user not match (apply: %s, query: %s)",
            task_id,
            schema_in.user_id,
            user_id,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="模拟交易的用户信息不一致！！！"
        )
    # get backtest task_id
    row = await client.execute_query_dict(
        "SELECT task_id FROM wk_strategy_backtest WHERE id=%s", backtest_id
    )
    if len(row) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="没找到对应的回测信息"
        )
    bt_task_id = str(row[0]["task_id"])

    if schema_in.market_id:
        market = await StrategyMarket.get(id=schema_in.market_id)
    else:
        market = None

    strategy = QStrategy(
        sim_id=schema_in.sim_id,
        user_id=user_id,
        task_id=task_id,
        sim_name=sim_name,
        bt_task_id=bt_task_id,
        sim_start_cash=sim_start_cash,
        sim_start_dt=sim_start_dt,
        status=ListStatus.online_review,
        name=schema_in.name,
        category=schema_in.category,
        style=schema_in.style,
        tags=schema_in.tags,
        ideas=schema_in.ideas if schema_in.ideas else "",
        desc=schema_in.desc if schema_in.desc else "",
        suit_money=schema_in.suit_money,
        buyout_price=jsonable_encoder(
            schema_in.buyout_price if schema_in.buyout_price else []
        ),
        total_cnt=schema_in.total_cnt,
        period_prices=jsonable_encoder(
            schema_in.period_prices if schema_in.period_prices else []
        ),
        market=market,
        limit_copy=1,
        limit_interval=1,
    )
    await strategy.save()
    review = ReviewRecord(
        product_id=strategy.product_id,
        product_type=ProductType.qstrategy,
        operation=ReviewOP.online,
        review_status=ReviewStatus.wait,
        review_msg=schema_in.msg if schema_in.msg else "",
        user_id=user_id,  # 申请人
        contact=schema_in.contact,  # 申请人手机号
        market=market,
    )
    await review.save()
    return CommonOut()


@router.post("/apply/strategy/delist", response_model=CommonOut, tags=["后台——上下架申请"])
async def delist_apply(query_in: OfflineApplyInfo):
    """策略下架申请"""
    client = Tortoise.get_connection("qpweb")
    # get simulation info
    row = await client.execute_query_dict(
        "SELECT user_id FROM wk_simulation WHERE id=%s", query_in.sim_id,
    )
    if len(row) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请检查查询参数")
    # get user
    user_id = str(row[0]["user_id"])
    row = await client.execute_query_dict(
        "SELECT phone FROM wk_user WHERE id=%s", user_id
    )
    if len(row) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请检查查询参数")
    user_phone = row[0]["phone"]
    if query_in.user_id != user_phone:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请检查查询参数")

    strategy = await QStrategy.filter(sim_id=query_in.sim_id).get_or_none()
    if not strategy:
        logger.error("delist apply with strategy not in market: %s", query_in)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="请检查查询参数")
    strategy.status = ListStatus.offline_review
    await strategy.save()
    review = ReviewRecord(
        product_id=strategy.product_id,
        product_type=ProductType.qstrategy,
        operation=ReviewOP.offline,
        review_status=ReviewStatus.wait,
        review_msg=query_in.msg,
        user_id=user_id,  # 申请人
        contact=query_in.contact,  # 申请人手机号
        market=strategy.market,
    )
    await review.save()
    return CommonOut()
