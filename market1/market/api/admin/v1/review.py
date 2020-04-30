import logging

from fastapi import APIRouter, Depends
from tortoise.exceptions import DoesNotExist
from tortoise.query_utils import Q

from market.core.security import require_super_scope_admin, require_super_scope_su
from market.models.admin_user import MarketAdminUser
from market.models.const import ListStatus, ProductType, ReviewOP, ReviewStatus
from market.models.package import StrategyPackage
from market.models.review import ReviewRecord
from market.models.strategy import QStrategy
from market.schemas.base import CommonOut
from market.schemas.review import (
    ReviewInfo,
    ReviewResult,
    ReviewSearch,
    ReviewSearchOut,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/review/find", response_model=ReviewSearchOut, tags=["后台——上下架审核管理"])
async def search_review(
    schema_in: ReviewSearch,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """查找申请"""
    query = ReviewRecord.filter()
    if schema_in.review_id:
        query = query.filter(id=schema_in.review_id)
    if schema_in.review_status:
        query = query.filter(review_status=schema_in.review_status)
    else:
        query = query.filter(~Q(review_status=ReviewStatus.deleted))
    if schema_in.operation:
        query = query.filter(operation=schema_in.operation)
    if schema_in.market_id:
        query = query.filter(market__id=schema_in.market_id)
    if schema_in.user_id:
        query = query.filter(user_id=schema_in.user_id)
    if schema_in.product_type:
        query = query.filter(product_type=schema_in.product_type)
    if schema_in.product_id:
        query = query.filter(product_id__contains=schema_in.product_id)
    if schema_in.contact:
        query = query.filter(contact__contains=schema_in.product_id)

    total_count = await query.count()
    review_list = (
        await query.order_by("update_dt")
        .offset(schema_in.offset)
        .limit(schema_in.count)
    )
    strategy_ids = []
    package_ids = []
    for review in review_list:
        if review.product_type == ProductType.qstrategy:
            strategy_ids.append(review.product_id)
        else:
            package_ids.append(review.product_id)
    strategies = await QStrategy.filter(product_id__in=strategy_ids)
    pkgs = await StrategyPackage.filter(product_id__in=package_ids)
    extras = {}
    for strategy in strategies:
        extras[strategy.product_id] = {
            "name": strategy.name,
            "sim_name": strategy.sim_name,
            "task_id": strategy.task_id,
            "bt_task_id": strategy.bt_task_id,
            "sim_start_cash": strategy.sim_start_cash,
            "sim_start_dt": strategy.sim_start_dt,
            "category": strategy.category,
        }
    for pkg in pkgs:
        extras[pkg.product_id] = {"name": pkg.name}
    return ReviewSearchOut(
        total=total_count,
        data=[
            {**review.__dict__, **extras.get(review.product_id, {})}
            for review in review_list
        ],
    )


@router.post("/review/result", response_model=CommonOut, tags=["后台——上下架审核管理"])
async def do_review(
    schema_in: ReviewResult,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """审核结果：通过 / 拒绝"""
    try:
        review = await ReviewRecord.get(id=schema_in.id)
    except DoesNotExist:
        return CommonOut(errCode=-1, errMsg="操作失败，未找到对应的审核记录")
    if review.review_status != ReviewStatus.wait:
        return CommonOut(errCode=-2, errMsg="操作失败，已完成审核")

    try:
        if review.product_type == ProductType.qstrategy:
            product = await QStrategy.get(product_id=review.product_id)
        elif review.product_type == ProductType.package:
            product = await StrategyPackage.get(product_id=review.product_id)
    except DoesNotExist:
        return CommonOut(errCode=-2, errMsg="操作失败，没找到对应的策略 / 套餐")

    if product.status not in (ListStatus.online_review, ListStatus.offline_review):
        return CommonOut(errCode=-2, errMsg="操作失败，策略 / 套餐已完成审核")

    review.review_msg = schema_in.msg
    if schema_in.accept:
        review.review_status = ReviewStatus.accepted
        if review.operation == ReviewOP.online:
            product.status = ListStatus.online
        else:
            product.status = ListStatus.offline
    else:
        review.review_status = ReviewStatus.rejected
        if review.operation == ReviewOP.online:
            product.status = ListStatus.online_rejected
        else:
            product.status = ListStatus.offline_rejected
    await review.save()
    await product.save()
    return CommonOut()


@router.get("/review/{review_id}", response_model=ReviewInfo, tags=["后台——上下架审核管理"])
async def show_review(
    review_id: int, current_user: MarketAdminUser = Depends(require_super_scope_su),
):
    """查看策略申请"""
    review = await ReviewRecord.get(id=review_id)
    extras = {}
    if review.product_type == ProductType.qstrategy:
        strategy = await QStrategy.get_or_none(product_id__in=review.product_id)
        if strategy:
            extras.update(
                {
                    "name": strategy.name,
                    "sim_name": strategy.sim_name,
                    "task_id": strategy.task_id,
                    "bt_task_id": strategy.bt_task_id,
                    "sim_start_cash": strategy.sim_start_cash,
                    "sim_start_dt": strategy.sim_start_dt,
                    "category": strategy.category,
                }
            )
    else:
        pkg = await StrategyPackage.get_or_none(product_id__in=review.product_id)
        if pkg:
            extras["name"] = pkg.name

    return ReviewInfo(**review.__dict__, **extras)
