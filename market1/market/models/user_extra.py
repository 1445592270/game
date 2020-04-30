from tortoise import fields

from market.models.base import Base
from market.models.const import UserStatus


class MarketUserExtra(Base):
    """用户信息"""

    uid = fields.ForeignKeyField(
        "market.MarketUser", "extras", on_delete=fields.CASCADE
    )
    coupons = fields.JSONField()  # list of coupon ids
    wechat_info = fields.JSONField()  # 微信联合登录
