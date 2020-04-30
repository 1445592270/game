import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from tortoise.query_utils import Q

from market.api.share.strategy import (
    change_strategy_status,
    edit_strategy,
    search_strategy,
    show_strategy,
)
from market.core.security import require_super_scope_admin, require_super_scope_su
from market.models.admin_user import MarketAdminUser
from market.models.const import ListStatus
from market.models.strategy import QStrategy
from market.schemas.base import CommonOut
from market.schemas.strategy import (
    QStrategyInfo,
    QStrategySearch,
    QStrategySearchOut,
    QStrategyStatusOp,
    QStrategyUpdateIn,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/strategy/edit", response_model=CommonOut, tags=["后台——策略管理"])
async def admin_edit_strategy(
    schema_in: QStrategyUpdateIn,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """编辑上架策略"""
    return await edit_strategy(schema_in.product_id, schema_in.changed)


@router.post("/strategy/del", response_model=CommonOut, tags=["后台——策略管理"])
async def del_strategy(
    schema_in: QStrategyStatusOp,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """删除策略，在上架状态不能直接删除"""
    id_list = schema_in.product_id
    if isinstance(id_list, str):
        id_list = [id_list]
    await QStrategy.filter(~Q(status=ListStatus.online), product_id__in=id_list).update(
        status=ListStatus.deleted
    )
    return CommonOut()


@router.post("/strategy/enable", response_model=CommonOut, tags=["后台——策略管理"])
async def enable_strategy(
    schema_in: QStrategyStatusOp,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """直接重新上架策略"""
    return await change_strategy_status(schema_in.product_id, ListStatus.online)


@router.post("/strategy/disable", response_model=CommonOut, tags=["后台——策略管理"])
async def disable_strategy(
    schema_in: QStrategyStatusOp,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """直接下架策略"""
    return await change_strategy_status(schema_in.product_id, ListStatus.offline)


@router.post("/strategy/find", response_model=QStrategySearchOut, tags=["后台——策略管理"])
async def admin_search_strategy(
    schema_in: QStrategySearch,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """搜索策略"""
    return await search_strategy(schema_in)


@router.get("/strategy/{strategy_id}", response_model=QStrategyInfo, tags=["后台——策略管理"])
async def admin_show_strategy(
    strategy_id: UUID, current_user: MarketAdminUser = Depends(require_super_scope_su),
):
    """查看策略"""
    return await show_strategy(strategy_id)
