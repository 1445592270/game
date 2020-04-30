from tortoise import fields

from market.models.base import Base
from market.models.const import ProductType, ReviewOP, ReviewStatus


class ReviewRecord(Base):
    """上下架审核记录表"""

    id = fields.IntField(pk=True)
    market = fields.ForeignKeyField(
        "market.StrategyMarket", "reviews", on_delete=fields.SET_NULL, null=True
    )
    product_id = fields.UUIDField(index=True)  # 商品 ID
    product_type = fields.IntEnumField(ProductType)  # 商品类型：1= 策略，2= 套餐，3=vip
    create_dt = fields.DatetimeField(auto_now_add=True)
    update_dt = fields.DatetimeField(auto_now=True)
    operation = fields.IntEnumField(ReviewOP)  # 操作类型：1= 上架，2= 下架
    user_id = fields.IntField()  # 申请人
    contact = fields.CharField(max_length=14)  # 申请人手机号
    # 审核
    review_status = fields.IntEnumField(ReviewStatus, default=1)  # 审核状态
    review_dt = fields.DatetimeField(null=True)
    review_msg = fields.TextField(null=True)  # 审核备注
