from tortoise import fields

from market.models.base import Base
from market.models.const import UserScope2, UserStatus


class MarketAdminUser(Base):
    """策略市场管理员表"""

    id = fields.IntField(pk=True)
    uuid = fields.UUIDField(null=False, index=True)
    name = fields.CharField(max_length=32, unique=True)
    phone = fields.CharField(max_length=14, unique=True)
    email = fields.CharField(max_length=63, unique=True)
    password = fields.CharField(max_length=128)
    scope1 = fields.CharField(max_length=32)  # 管理员职权范围（超市级别）
    scope2 = fields.IntEnumField(UserScope2)  # 管理员职权范围（超市内级别）
    status = fields.IntEnumField(UserStatus, default=UserStatus.normal)
    create_dt = fields.DatetimeField(auto_now_add=True)  # 创建时间
    update_dt = fields.DatetimeField(auto_now=True)

    def is_active(self):
        return self.status == 1
