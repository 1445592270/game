from tortoise import fields

from market.models.base import Base
from market.models.const import TagType


class Tag(Base):
    """标签"""

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=32, unique=True, index=True)
    tag_type = fields.IntEnumField(TagType, default=1)  # 标签类型：1= 标签，2= 风格
    create_dt = fields.DatetimeField(auto_now_add=True)  # 创建时间
    update_dt = fields.DatetimeField(auto_now=True)
    deleted = fields.BooleanField(default=False)  # 删除标记
