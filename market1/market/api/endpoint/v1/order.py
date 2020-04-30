import datetime
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder

from market.api.share.order import search_order
from market.core.security import require_active_user
from market.models.const import ListStatus, OrderStatus, ProductType
from market.models.order import UserOrder
from market.models.package import StrategyPackage
from market.models.strategy import QStrategy
from market.models.user import MarketUser
from market.schemas.base import CommonOut
from market.schemas.order import (
    OrderCancel,
    OrderCreate,
    OrderInfo,
    OrderSearch,
    OrderSearchOut,
)
from market.schemas.package import PkgInfo
from market.schemas.strategy import QStrategyInfo

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/order/calc-price", response_model=CommonOut, tags=["用户端——订单管理"])
async def calc_price(
    order_in: OrderCreate, current_user: MarketUser = Depends(require_active_user)
):
    """计算订单的总价格"""
    pass


@router.post("/order/submit", response_model=CommonOut, tags=["用户端——订单管理"])
async def submit_order(
    order_in: OrderCreate, current_user: MarketUser = Depends(require_active_user)
):
    """用户下单"""
    # get_prod_info
    if order_in.product_type == ProductType.qstrategy:
        product = await QStrategy.get_or_none(product_id=order_in.product_id)
        snapshot = QStrategyInfo(**product.__dict__).dict()
    else:
        product = await StrategyPackage.get_or_none(product_id=order_in.product_id)
        snapshot = PkgInfo(**product.__dict__).dict()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="没找到对应的商品（策略 / 套餐）",
        )
    # calculate price
    if product.status != ListStatus.online:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="商品（策略 / 套餐）已下线",
        )

    has_price = False
    # 订单金额
    total_cash = 0
    # 订购总时长
    total_days = order_in.days + order_in.gift_days
    # 优惠券抵扣金额
    coupon_cash = 0
    # 优惠券抵扣时长
    coupon_days = 0
    # 开启折扣，且订单的赠送时长为 0
    # 毫秒时间戳
    now = datetime.datetime.now().timestamp() * 1000
    if product.enable_discount and order_in.gift_days == 0:
        for discount_info in product.discount_info:
            if now < discount_info.start_ts or now > discount_info.end_ts:
                continue
            if discount_info.day == order_in.days:
                total_cash = discount_info.price
                has_price = True
                break
    if not has_price:
        for price_info in product.period_prices:
            if price_info.get("day", 0) == order_in.days:
                # and price_info.get("gift_day", 0) == order_in.gift_days
                total_cash = price_info.get("price", 0)
                has_price = True
                break
    if not has_price:
        total_cash = product.buyout_price
        has_price = True
        # raise HTTPException(
        #     status_code=status.HTTP_404_NOT_FOUND, detail="未找到商品（策略 / 套餐）针对该时长的价格信息",
        # )
    if product.allow_coupon and order_in.coupons:
        for coupon_id in order_in.coupons:
            # TODO: 判断该优惠券是否启用，用户是否拥有该优惠券
            pass

    # return {
    #     "total_cash": total_cash,
    #     "total_days": total_days,
    #     "coupon_cash": coupon_cash,
    #     "coupon_days": coupon_days,
    # }
    db_user = await MarketUser.get(id=current_user.id)
    expire_dt = datetime.datetime.now() + datetime.timedelta(
        days=total_days + coupon_days
    )
    user_order = await UserOrder.create(
        **order_in.dict(),
        user=db_user,
        total_cash=total_cash,
        total_days=total_days,
        coupon_days=coupon_days,
        coupon_cash=coupon_cash,
        pay_cash=max(0, total_cash - coupon_cash),
        payed_cash=0,
        product_snapshot=jsonable_encoder(snapshot),
        expire_dt=expire_dt
        # coupon=[],
        # TODO: expire_dt 在完成支付时设置
    )
    # TODO: get pay url
    return OrderInfo(**user_order.__dict__)


@router.post("/order/cancel", response_model=CommonOut, tags=["用户端——订单管理"])
async def cancel_order(
    schema_in: OrderCancel, current_user: MarketUser = Depends(require_active_user)
):
    """用户取消订单，发生支付前"""
    if isinstance(schema_in.id, int):
        order_id = schema_in.id
    else:
        order_id = schema_in.id[0]
    order = await UserOrder.get_or_none(id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="未找到该订单",
        )
    if order.status != OrderStatus.unpayed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="订单已完成",
        )
    # TODO: 取消支付
    order.status = OrderStatus.calceled
    await order.save()
    return CommonOut()


@router.post("/order/search", response_model=OrderSearchOut, tags=["用户端——订单管理"])
async def user_search_order(
    schema_in: OrderSearch, current_user: MarketUser = Depends(require_active_user),
):
    """用户查看自己的订单列表"""
    schema_in.user_id = current_user.id
    return await search_order(schema_in)
