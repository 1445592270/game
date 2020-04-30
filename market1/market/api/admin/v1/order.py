import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException
from tortoise.exceptions import DoesNotExist

from market.api.share.order import search_order, show_order
from market.core.security import require_super_scope_admin
from market.models.admin_user import MarketAdminUser
from market.models.const import OrderStatus, PayMethod
from market.models.order import UserOrder
from market.schemas.base import CommonOut
from market.schemas.order import OrderInfo, OrderSearch, OrderSearchOut

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/order/search", response_model=OrderSearchOut, tags=["后台——订单管理"])
async def admin_search_order(
    schema_in: OrderSearch,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """策略上架申请"""
    return await search_order(schema_in)


@router.get("/order/{order_id}", response_model=OrderInfo, tags=["后台——订单管理"])
async def admin_show_order(
    order_id: int, current_user: MarketAdminUser = Depends(require_super_scope_admin)
):
    """查看标签或者风格"""
    return await show_order(order_id)


@router.post("/pay/confirm/{order_id}", response_model=CommonOut, tags=["后台——订单管理"])
async def confirm_pay(
    order_id: int, current_user: MarketAdminUser = Depends(require_super_scope_admin)
):
    """确认支付（线下订单）"""
    try:
        order = await UserOrder.get(id=order_id)
    except DoesNotExist:
        raise HTTPException(404, detail="订单未找到")
    if order.pay_method != PayMethod.offline:
        raise HTTPException(400, detail="仅线下支付订单支持支付确认")
    if order.status != OrderStatus.unpayed:
        raise HTTPException(400, detail="订单已支付 / 取消")
    order.payed_cash = order.pay_cash
    order.pay_dt = datetime.datetime.now()
    order.expire_dt = datetime.datetime.now() + datetime.timedelta(
        days=order.total_days + order.coupon_days
    )
    order.status = OrderStatus.payed
    await order.save()
    return CommonOut()


@router.post("/pay/cancel/{order_id}", response_model=CommonOut, tags=["后台——订单管理"])
async def cancel_pay(
    order_id: int, current_user: MarketAdminUser = Depends(require_super_scope_admin)
):
    """取消支付（线下订单）"""
    try:
        order = await UserOrder.get(id=order_id)
    except DoesNotExist:
        raise HTTPException(404, detail="订单未找到")
    if order.pay_method != PayMethod.offline:
        raise HTTPException(400, detail="仅线下支付订单支持支付确认")
    if order.status != OrderStatus.unpayed:
        raise HTTPException(400, detail="订单已支付 / 取消")
    order.status = OrderStatus.calceled
    await order.save()
    return CommonOut()
