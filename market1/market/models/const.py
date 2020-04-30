from enum import Enum, IntEnum

# 总站的 scope1 值
SUPER_SCOPE = "aq"


class PayMethod(IntEnum):
    """推送方式"""

    offline = 1  # 线下支付
    wechat = 2  # 微信支付
    # alipay = 2  # 支付宝支付


class CouponCategory(IntEnum):
    """优惠券类型"""

    deduce_day = 1  # 抵扣时长
    deduce_cash = 2  # 抵扣金额
    cash_discount = 3  # 金额打折


class UserStatus(IntEnum):
    """用户状态"""

    normal = 1  # 正常
    inactive = 2  # 未激活
    disabled = 3  # 禁用
    deleted = 4  # 注销


class UserScope2(IntEnum):
    """管理员权限类别"""

    su = 1  # 超级管理员


class TagType(IntEnum):
    """标签的类型"""

    tag = 1  # 标签
    style = 2  # 风格


class ListStatus(IntEnum):
    """商品的展示状态"""

    online_review = 1  # 上架审核中
    online_rejected = 2  # 上架审核未通过
    online = 3  # 正常
    offline_review = 4  # 下架审核中
    offline_rejected = 5  # 下架审核中
    offline = 6  # 下架
    deleted = 7  # 删除


class QStrategyType(IntEnum):
    """策略类型"""

    stock = 1  # 股票策略
    futures = 2  # 期货策略


class MarketStatus(IntEnum):
    """超市状态"""

    normal = 1
    disabled = 2
    deleted = 3  # 删除


class PushMethod(IntEnum):
    """推送方法"""

    wechat = 1  # 微信
    email = 2  # 邮箱
    post = 3  # post 到指定 url


class PushStatus(IntEnum):
    """推送状态"""

    normal = 1  # 推送
    disabled = 2  # 禁用 / 关闭
    expired = 3  # 到期


class ProductType(IntEnum):
    """product_type"""

    qstrategy = 1  # 策略
    package = 2  # 套餐
    vip = 3  # vip


class OrderStatus(IntEnum):
    """订单状态"""

    unpayed = 1  # 待支付
    payed = 2  # 支付成功
    calceled = 3  # 取消支付
    expierd = 4  # 超时
    deleted = 9  # 删除标记


class ReviewOP(IntEnum):
    """审核类型"""

    online = 1  # 上架
    offline = 2  # 下架


class ReviewStatus(IntEnum):
    """审核状态"""

    wait = 1  # 待审核
    accepted = 2  # 审核通过
    rejected = 3  # 审核被拒
    deleted = 4  # 删除
