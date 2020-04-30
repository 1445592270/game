from tortoise import fields

from market.models.base import Base
from market.models.const import UserStatus


class MarketUser(Base):
    """策略市场用户表"""

    id = fields.IntField(pk=True)
    uuid = fields.UUIDField(null=False, index=True)
    name = fields.CharField(max_length=32, unique=True)
    phone = fields.CharField(max_length=14, unique=True, null=True)
    email = fields.CharField(max_length=63, unique=True, null=True)
    market = fields.ForeignKeyField(
        "market.StrategyMarket", "users", on_delete=fields.SET_NULL, null=True
    )
    broker_id = fields.CharField(max_length=32, null=True)  # 代理商 ID
    password = fields.CharField(max_length=128)
    status = fields.IntEnumField(UserStatus, default=1)  # 帐号状态：1= 正常，2= 禁用，3= 注销

    def is_active(self):
        return self.status == 1
