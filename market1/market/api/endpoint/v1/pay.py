import logging

from fastapi import APIRouter, Depends

from market.core.security import require_active_user
from market.models.user import MarketUser
from market.schemas.order import OrderSearchOut

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/pay/query", response_model=OrderSearchOut, tags=["用户端——支付管理"])
async def query_pay(current_user: MarketUser = Depends(require_active_user)):
    """用户查询订单支付状态"""


@router.post("/refund", response_model=OrderSearchOut, tags=["用户端——支付管理"])
async def refund(current_user: MarketUser = Depends(require_active_user)):
    """用户退款申请"""


@router.post("/refund/query", response_model=OrderSearchOut, tags=["用户端——支付管理"])
async def query_refund(current_user: MarketUser = Depends(require_active_user)):
    """用户退款查询"""
