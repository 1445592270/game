from tortoise import fields

from market.models.base import Base
from market.models.const import OrderStatus, PayMethod, ProductType


class UserOrder(Base):
    """用户订单表"""

    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "market.MarketUser", "orders", on_delete=fields.SET_NULL, null=True
    )
    product_id = fields.UUIDField(index=True)  # 商品 ID
    product_type = fields.IntEnumField(ProductType)  # 商品类型：1= 策略，2= 套餐，3=vip
    status = fields.IntEnumField(
        OrderStatus, default=OrderStatus.unpayed
    )  # 订单状态：1= 待支付，2= 支付成功，3= 支付失败，4= 取消支付 / 超时
    total_cash = fields.FloatField(default=0)  # 订单总金额
    total_days = fields.IntField(default=0)  # 订单总天数
    coupon_days = fields.IntField(default=0)  # 优惠券抵扣天数
    coupon_cash = fields.FloatField(default=0)  # 优惠券优惠金额
    pay_cash = fields.FloatField(default=0)  # 订单需支付金额
    days = fields.IntField(default=0)  # 购买时长
    gift_days = fields.IntField(default=0)  # 赠送时长
    expire_dt = fields.DatetimeField(null=True)  # 过期时间
    create_dt = fields.DatetimeField(auto_now_add=True)  # 创建时间
    update_dt = fields.DatetimeField(auto_now=True)
    foreign_order_id = fields.CharField(max_length=32, default="")  # 外部订单号
    pay_id = fields.CharField(max_length=48, default="")  # 支付平台订单号
    pay_method = fields.IntEnumField(PayMethod, default=PayMethod.wechat)
    pay_url = fields.CharField(max_length=255, default="")  # 支付链接（重新支付）
    pay_dt = fields.DatetimeField(null=True)  # 支付时间
    payed_cash = fields.FloatField(default=0)  # 已支付金额
    source = fields.CharField(max_length=32, default="default")  # 订单来源：pc/mobile
    delete = fields.BooleanField(default=False)
    coupon = fields.JSONField(default=[])  # 使用的优惠券
    product_snapshot = fields.JSONField(default={})  # 商品快照
