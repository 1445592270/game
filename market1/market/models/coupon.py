from tortoise import fields

from market.models.base import Base
from market.models.const import CouponCategory


class Coupon(Base):
    """优惠券"""

    id = fields.IntField(pk=True)
    category = fields.IntEnumField(CouponCategory)
    value = fields.FloatField(default=0)
    total_cnt = fields.IntField(default=0)
    limit_cnt = fields.IntField(default=1)  # 每人限领数量
    disable = fields.BooleanField(default=False)
    start_dt = fields.DatetimeField(auto_now_add=True)  # 开始时间
    expire_dt = fields.DatetimeField()
    create_dt = fields.DatetimeField(auto_now_add=True)  # 创建时间
    msg = fields.TextField()
