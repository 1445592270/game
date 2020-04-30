import datetime
from typing import List, Optional, Union
from uuid import UUID

from fastapi import Query

from market.models.const import OrderStatus, PayMethod, ProductType
from market.schemas.base import BaseSearch, CommonOut, CustomBaseModel, SearchStr


class OrderInfo(CustomBaseModel):
    id: int
    product_id: UUID
    # 商品类型：1= 策略，2= 套餐，3=vip
    product_type: ProductType
    # 订单状态：1= 待支付，2= 支付成功，3= 支付失败，4= 取消支付 / 超时
    status: OrderStatus

    total_cash: float = Query(..., ge=0)  # 订单总金额
    total_days: float = Query(..., ge=0)  # 订单总天数
    coupon_days: float = Query(..., ge=0)  # 优惠券抵扣天数
    coupon_cash: float = Query(..., ge=0)  # 优惠券优惠金额
    pay_cash: float = Query(..., ge=0)  # 订单金额
    payed_cash: float = Query(..., ge=0)
    pay_dt: Optional[datetime.datetime]
    days: int = Query(..., gt=0)
    gift_days: int = Query(..., ge=0)  # 赠送时长
    expire_dt: Optional[datetime.datetime]
    create_dt: Optional[datetime.datetime]
    foreign_order_id: str = Query(default="", min_length=0, max_length=32)  # 外部订单号
    pay_id: str = Query(default="", min_length=0, max_length=48)  # 支付平台订单号
    pay_method: PayMethod
    pay_url: str = Query(default="", min_length=0, max_length=255)  # 支付链接（重新支付）
    source: str = Query(default="", min_length=0, max_length=32)  # 订单来源：pc/mobile
    coupon: List[int] = []
    # product_snapshot = fields.JSONField(default={})  # 商品快照

    class Config:
        orm_mode = True


class OrderCreate(CustomBaseModel):
    product_id: str
    product_type: ProductType = ProductType.qstrategy  # 商品类型：1= 策略，2= 套餐，3=vip
    days: int = Query(..., gt=0)
    gift_days: int = Query(default=0, ge=0)  # 赠送时长
    source: str = Query(default="pc", min_length=0, max_length=32)  # 订单来源：pc/mobile
    coupons: Optional[List[int]]
    pay_method: PayMethod

    class Config:
        schema_extra = {
            "example": {
                "product_id": "123",
                "product_type": 1,
                "days": 10,
                "gift_days": 10,
                "pay_method": PayMethod.offline,
            }
        }


class OrderCancel(CustomBaseModel):
    id: Union[int, List[int]]

    class Config:
        schema_extra = {"example": {"id": [1, 2, 3]}}


class OrderDel(OrderCancel):
    pass


class SearchOrder(CustomBaseModel):
    id: int
    user_id: int
    user_name: str
    user_phone: str
    product_id: UUID
    # 商品类型：1= 策略，2= 套餐，3=vip
    product_type: ProductType
    # 订单状态：1= 待支付，2= 支付成功，3= 支付失败，4= 取消支付 / 超时
    status: OrderStatus

    total_cash: float = Query(..., ge=0)  # 订单总金额
    total_days: float = Query(..., ge=0)  # 订单总天数
    coupon_days: float = Query(..., ge=0)  # 优惠券抵扣天数
    coupon_cash: float = Query(..., ge=0)  # 优惠券优惠金额
    pay_cash: float = Query(..., ge=0)  # 订单金额
    payed_cash: float = Query(..., ge=0)
    pay_dt: Optional[datetime.datetime]
    days: int = Query(..., gt=0)
    gift_days: int = Query(..., ge=0)  # 赠送时长
    expire_dt: Optional[datetime.datetime]
    create_dt: Optional[datetime.datetime]
    foreign_order_id: str = Query(default="", min_length=0, max_length=32)  # 外部订单号
    pay_id: str = Query(default="", min_length=0, max_length=48)  # 支付平台订单号
    pay_method: PayMethod
    pay_url: str = Query(default="", min_length=0, max_length=255)  # 支付链接（重新支付）
    source: str = Query(default="", min_length=0, max_length=32)  # 订单来源：pc/mobile
    coupon: List[int] = []
    # product_snapshot = fields.JSONField(default={})  # 商品快照

    class Config:
        orm_mode = True


class OrderSearch(BaseSearch):
    user_id: Optional[int]
    order_id: Optional[int]
    product_id: Optional[SearchStr]
    # 商品类型：1= 策略，2= 套餐，3=vip
    product_type: Optional[ProductType]
    # 订单状态：1= 待支付，2= 支付成功，3= 支付失败，4= 取消支付 / 超时
    status: Optional[OrderStatus]

    class Config:
        schema_extra = {"example": {"user_id": 1, "offset": 0, "count": 100}}


class OrderSearchOut(CommonOut):
    data: List[SearchOrder] = []
