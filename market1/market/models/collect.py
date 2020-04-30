from tortoise import fields

from market.models.base import Base
from market.models.const import ProductType


class UserCollection(Base):
    """用户收藏列表"""

    id = fields.IntField(pk=True)
    url = fields.CharField(max_length=512)
    product_id = fields.UUIDField(index=True)  # 商品 ID
    product_type = fields.IntEnumField(ProductType)  # 商品类型：1= 策略，2= 套餐，3=vip
    user_id = fields.IntField()
    canceled = fields.BooleanField(default=False)  # 收藏状态：1= 正常，2= 取消收藏
