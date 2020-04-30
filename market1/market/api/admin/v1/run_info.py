import logging

from fastapi import APIRouter, Depends

from market.core.security import require_super_scope_admin
from market.models.admin_user import MarketAdminUser
from market.schemas.base import CommonOut

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/runinfo/curve/{task_type}/{task_id}", response_model=CommonOut, tags=["后台——运行信息"]
)
async def get_curves(
    task_type: str,
    task_id: str,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """获取收益曲线

    :param task_type: sim/bt/compile
    :param task_id: xxxx
    """


@router.get(
    "/runinfo/order/{task_type}/{task_id}", response_model=CommonOut, tags=["后台——运行信息"]
)
async def get_orders(
    task_type: str,
    task_id: str,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """获取下单信息

    :param task_type: sim/bt/compile
    :param task_id: xxxx
    """


@router.get(
    "/runinfo/position/{task_type}/{task_id}", response_model=CommonOut, tags=["后台——运行信息"]
)
async def get_positions(
    task_type: str,
    task_id: str,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """获取持仓信息

    :param task_type: sim/bt/compile
    :param task_id: xxxx
    """


@router.get(
    "/runinfo/indicator/{task_type}/{task_id}",
    response_model=CommonOut,
    tags=["后台——运行信息"],
)
async def get_indicators(
    task_type: str,
    task_id: str,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """获取技术指标信息

    :param task_type: sim/bt/compile
    :param task_id: xxxx
    """


@router.get(
    "/runinfo/top/{task_type}/{task_id}", response_model=CommonOut, tags=["后台——运行信息"]
)
async def get_top_orders(
    task_type: str,
    task_id: str,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """获取模拟交易的牛股（收益高的订单）

    :param task_type: sim/bt/compile
    :param task_id: xxxx
    """
