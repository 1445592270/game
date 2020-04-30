import logging

from fastapi import APIRouter, Depends, HTTPException, status

from market.core.security import require_super_scope_admin, require_super_scope_su
from market.models.admin_user import MarketAdminUser
from market.models.const import MarketStatus
from market.models.market import StrategyMarket
from market.schemas.base import CommonOut
from market.schemas.market import (
    MarketCreate,
    MarketDisable,
    MarketInfo,
    MarketSearch,
    MarketSearchOut,
    MarketUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/market/new", response_model=CommonOut, tags=["后台——超市管理"])
async def add_market(
    schema_in: MarketCreate,
    current_user: MarketAdminUser = Depends(require_super_scope_su),
):
    """添加新的策略超市"""
    await StrategyMarket.create(**schema_in.dict(), status=MarketStatus.normal)
    return CommonOut()


@router.post("/market/edit", response_model=CommonOut, tags=["后台——超市管理"])
async def edit_market(
    schema_in: MarketUpdate,
    current_user: MarketAdminUser = Depends(require_super_scope_su),
):
    """编辑策略超市信息"""
    market = await StrategyMarket.get_or_none(id=schema_in.id)
    if not market:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="未找到要编辑的策略")
    if schema_in.name:
        market.name = schema_in.name
    if schema_in.domain:
        market.domain = schema_in.domain
    await market.save()
    return CommonOut()


@router.post("/market/disable", response_model=CommonOut, tags=["后台——超市管理"])
async def disable_market(
    schema_in: MarketDisable,
    current_user: MarketAdminUser = Depends(require_super_scope_su),
):
    """禁用 / 删除超市"""
    id_list = schema_in.id
    if isinstance(id_list, int):
        id_list = [id_list]
    await StrategyMarket.filter(id__in=id_list).update(status=schema_in.status)
    return CommonOut()


@router.post("/market/find", response_model=MarketSearchOut, tags=["后台——超市管理"])
async def search_market(
    schema_in: MarketSearch,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """查找超市"""
    query = StrategyMarket.filter(status=MarketStatus.normal)
    if schema_in.id:
        query = query.filter(id=schema_in.id)
    if schema_in.name:
        query = query.filter(name__contains=schema_in.name)
    total_count = await query.count()
    markets = (
        await query.order_by("name").offset(schema_in.offset).limit(schema_in.count)
    )
    return MarketSearchOut(total=total_count, data=[market for market in markets])


@router.get("/market/{market_id}", response_model=MarketInfo, tags=["后台——超市管理"])
async def show_market(
    market_id: int, current_user: MarketAdminUser = Depends(require_super_scope_admin)
):
    """查看超市详情"""
    return await StrategyMarket.get(id=market_id)
