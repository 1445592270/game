from enum import Enum

from market.core.config import PAY_PARAMS

from .wechat_pay import WeixinPay

wx_pay = WeixinPay(PAY_PARAMS)  # noqa


class PayMethod(Enum):
    """支付方法枚举"""

    wx = "WX"
    ali = "ALI"


class PayMode(Enum):
    """支付模式枚举"""

    WAP = "wap"
    APP = "app"
    PAGE = "page"
    js = "JS"


class PayException(Exception):
    """支付异常"""


class PayUnSupport(PayException):
    """不支持的支付方式异常"""


def pay(
    product_name: str,
    product_id: str,
    cash: float,
    order_no: str,
    method: PayMethod,
    mode: PayMode,
):
    """支付下单

    :param product_name: 商品名称
    :param product_id: 商品 ID
    :param cash: 金额
    :param order_no: 平台（外部）订单号
    :param method: 支付方法（平台）
    :param pattern: 支付模式
    """
    if method != PayMethod.wx:
        raise PayUnSupport("不支持的支付方法")
    if mode != PayMode.PAGE:
        raise PayUnSupport("不支持的支付模式")


def cancel_pay(order_no: str):
    """取消支付下单

    :param order_no: 平台（外部）订单号
    """


def pay_query(order_no: str):
    """支付查询

    :param order_no: 平台（外部）订单号
    """


def refund(order_no: str, refund_no: str):
    """申请退款

    :param order_no: 平台（外部）订单号
    :param refund_no: 退款申请号
    """


def refund_query(order_no: str, refund_no: str):
    """退款查询

    :param order_no: 平台（外部）订单号
    :param refund_no: 退款申请号
    """
