from tortoise import fields

from market.models.base import Base
from market.models.const import MarketStatus
from market.models.package import StrategyPackage
from market.models.strategy import QStrategy
from market.models.review import ReviewRecord
from market.models.user import MarketUser


class StrategyMarket(Base):
    """超市"""

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=64, unique=True, index=True)  # 名字
    domain = fields.CharField(max_length=128)  # 域名
    status = fields.IntEnumField(MarketStatus, default=1)  # 超市状态：1= 运行， 2= 停止
    # uuid = fields.UUIDField(unique=True, index=True)  # 超市用户端认证

    # reverse relations
    strategies: fields.ReverseRelation[QStrategy]
    packages: fields.ReverseRelation[StrategyPackage]
    reviews: fields.ReverseRelation[ReviewRecord]
    users: fields.ReverseRelation[MarketUser]
