from tortoise import fields

from market.models.base import Base
from market.models.const import ListStatus


class StrategyPackage(Base):
    """套餐表"""

    product_id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=64, unique=True, index=True)
    market = fields.ForeignKeyField(
        "market.StrategyMarket", "packages", on_delete=fields.SET_NULL, null=True
    )
    tags = fields.JSONField()
    desc = fields.TextField()
    status = fields.IntEnumField(ListStatus, default=1)  # 套餐状态：1= 正常，2= 下架，3= 删除

    limit_copy = fields.IntField()  # 连续复制次数
    limit_interval = fields.IntField()  # 复制间隔
    view_cnt = fields.IntField(default=0)  # 浏览次数
    collect_cnt = fields.IntField(default=0)  # 收藏次数
    share_cnt = fields.IntField(default=0)  # 分享次数

    buyout_price = fields.FloatField()  # 买断价格
    # 时段购买价格信息 [{"day": 20, "gift_day": 20, "price": 350}, ...]
    period_prices = fields.JSONField()
    enable_discount = fields.BooleanField(default=True)
    # 折扣信息 [{"start_dt": xxx, "end_dt": xxx, "day": 10, "gift_day": 10, "price": 200}, ...]
    discount_info = fields.JSONField()
    allow_coupon = fields.BooleanField()  # 是否可使用优惠券
    create_dt = fields.DatetimeField(auto_now_add=True)  # 最初申请上架时间
    update_dt = fields.DatetimeField(auto_now=True)
    online_dt = fields.DatetimeField(null=True)
    offline_dt = fields.DatetimeField(null=True)

    # reverse relations
    strategies: fields.ReverseRelation["market.models.QStrategy"]
