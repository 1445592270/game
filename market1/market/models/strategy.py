from tortoise import fields

from market.models.base import Base
from market.models.const import ListStatus, QStrategyType


class QStrategy(Base):
    """
    上架策略详细信息
    The User model
    """

    product_id = fields.UUIDField(pk=True)
    sim_id = fields.IntField(index=True)
    user_id = fields.IntField(index=True)
    author_name = fields.CharField(max_length=32)
    task_id = fields.CharField(max_length=32, index=True)  # 模拟交易的 ID
    sim_start_cash = fields.FloatField(default=0)  # 模拟交易的初始资金
    sim_start_dt = fields.DatetimeField()  # 模拟交易的开始时间
    sim_name = fields.CharField(max_length=128)

    bt_task_id = fields.CharField(max_length=32, index=True)  # 回测的 ID
    # 状态：1= 上架审核中，2= 上架审核未通过，3= 正常，4= 下架审核中，5= 下架，6= 删除
    status = fields.IntEnumField(ListStatus, default=1)
    market = fields.ForeignKeyField(
        "market.StrategyMarket", "strategies", on_delete=fields.SET_NULL, null=True
    )
    package = fields.ForeignKeyField(
        "market.StrategyPackage", "strategies", on_delete=fields.SET_NULL, null=True
    )
    name = fields.CharField(max_length=128)  # 策略名称
    buyout_price = fields.FloatField()  # 买断价格
    total_cnt = fields.IntField()  # 总份数
    category = fields.IntEnumField(QStrategyType, default=1)  # 策略类型，1= 股票，2= 期货
    style = fields.CharField(max_length=32, default="")  # 策略风格
    tags = fields.JSONField(defalt=[])  # 标签数组
    ideas = fields.TextField(default="")  # 策略思路
    desc = fields.TextField(default="")  # 描述
    suit_money = fields.FloatField(default=10000000)  # 适合资金
    # package_name = fields.CharField(max_length=50)  # 所属套餐

    limit_copy = fields.IntField(default=100000)  # 连续复制次数
    limit_interval = fields.IntField(default=10000000)  # 复制间隔
    sell_cnt = fields.IntField(default=0)  # 已销售数量
    sell_cnt_show = fields.IntField(default=0)  # 虚假的销量
    create_dt = fields.DatetimeField(auto_now_add=True)  # 最初申请上架时间
    update_dt = fields.DatetimeField(auto_now=True)
    online_dt = fields.DatetimeField(null=True)
    offline_dt = fields.DatetimeField(null=True)
    view_cnt = fields.IntField(default=0)  # 浏览次数
    collect_cnt = fields.IntField(default=0)  # 收藏次数
    share_cnt = fields.IntField(default=0)  # 分享次数

    # 时段购买价格信息 [{"day": 20, "gift_day": 20, "price": 350}, ...]
    period_prices = fields.JSONField(default=[])
    enable_discount = fields.BooleanField(default=True)
    # 折扣信息 [{"start_dt": xxx, "end_dt": xxx, "day": 10, "gift_day": 10, "price": 200}, ...]
    discount_info = fields.JSONField(default=[])
    allow_coupon = fields.BooleanField(default=True)  # 是否可使用优惠券
