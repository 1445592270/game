import datetime
from typing import List, Optional, Tuple, Union
from uuid import UUID

from fastapi import Query

from market.models.const import ListStatus, OrderStatus, QStrategyType
from market.schemas.base import BaseSearch, CommonOut, CustomBaseModel, SearchStr
from market.schemas.package import DiscountInfo, PriceInfo
from market.schemas.runinfo import Indicators


class QStrategyInfo(CustomBaseModel):
    product_id: Optional[UUID]
    user_id: int = Query(..., gt=0)
    author_name: Optional[str] = ""
    sim_id: int = Query(..., gt=0)
    sim_name: Optional[str]
    sim_start_cash: float
    sim_start_dt: datetime.datetime
    task_id: str = Query(..., max_length=32)
    bt_task_id: str = Query(..., max_length=32)
    status: ListStatus
    market_id: Optional[int]
    package_id: Optional[UUID]
    name: str = Query(default="", min_length=1, max_length=64)
    category: QStrategyType
    style: str = Query(default="", min_length=1, max_lenth=32)  # 策略风格
    tags: List[str] = []
    ideas: str = Query(default="", min_length=0, max_length=1024)  # 策略思路
    desc: str = Query(default="", min_length=0, max_length=1024)  # 策略思路
    suit_money: float = Query(..., gt=0)  # 适合资金
    buyout_price: float = Query(..., gt=0)  # 买断价格

    total_cnt: int = Query(..., gt=0)  # 总份数
    sell_cnt: int = Query(default=0, ge=0)  # 已销售数量
    sell_cnt_show: int = Query(default=0, ge=0)  # 虚假的销量

    limit_copy: int = -1
    limit_interval: int = -1
    view_cnt: int = 0
    collect_cnt: int = 0
    share_cnt: int = 0

    # 时段购买价格信息 [{"day": 20, "gift_day": 20, "price": 350}, ...]
    period_prices: List[PriceInfo] = []
    enable_discount: bool = False
    # 折扣信息 [{"start_dt": xxx, "end_dt": xxx, "day": 10, "gift_day": 10, "price": 200}, ...]
    discount_info: List[DiscountInfo] = []
    allow_coupon: bool = True

    class Config:
        orm_mode = True


class StrategyCreate(QStrategyInfo):
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "sim_id": 123,
                "user_id": 123,
                "task_id": "abc",
                "status": 1,
                "market_id": 1,
                "package_id": "uuid1",
                "name": "pkg1",
                "category": 1,
                "style": "好的风格",
                "tags": ["a", "b"],
                "ideas": "高买低卖",
                "desc": "包亏不包赚",
                "suit_money": 1000,
                "buyout_price": 20000,
                "total_cnt": 10000000,
                "sell_cnt": 100,
                "sell_cnt_show": 2000,
                "limit_copy": 1,
                "limit_interval": 20,
                "view_cnt": 0,
                "collect_cnt": 0,
                "share_cnt": 0,
                "period_prices": [
                    {"day": 10, "gift_day": 10, "price": 200},
                    {"day": 20, "gift_day": 20, "price": 350},
                ],
                # 时段购买价格信息 [{name: abc, day: 10, gift_day: 10, price: 200}...]
                "enable_discount": True,
                # 折扣信息 [{"start_dt": xxx, "end_dt": xxx, "day": 10, "gift_day": 10, "price": 200}, ...]
                "discount_info": [
                    {
                        "start_ts": 1234214,
                        "end_ts": 2143214124,
                        "price": 200,
                        "day": 10,
                        "gift_day": 10,
                    }
                ],
                "allow_coupon": True,
            }
        }


class QStrategyUpdateFields(CustomBaseModel):
    name: str = Query(..., min_length=1, max_length=64)
    package_id: Optional[UUID]
    market_id: int = Query(..., gt=0)
    tags: Optional[List[str]] = []
    category: QStrategyType = QStrategyType.stock
    style: Optional[str] = Query(..., min_length=1, max_lenth=32)  # 策略风格
    ideas: Optional[str] = Query(..., min_length=0, max_length=1024)  # 策略思路
    desc: Optional[str] = ""

    limit_copy: int = -1
    limit_interval: int = -1
    view_cnt: int = 0
    collect_cnt: int = 0
    share_cnt: int = 0

    suit_money: float = Query(..., gt=0)  # 适合资金
    buyout_price: float = Query(..., gt=0)  # 买断价格

    total_cnt: int = Query(..., gt=0)  # 总份数
    sell_cnt: int = Query(default=0, ge=0)  # 已销售数量
    sell_cnt_show: int = Query(default=0, ge=0)  # 虚假的销量

    # 时段购买价格信息 [{"day": 20, "gift_day": 20, "price": 350}, ...]
    period_prices: List[PriceInfo] = []
    enable_discount: bool = False
    # 折扣信息 [{"start_dt": xxx, "end_dt": xxx, "day": 10, "gift_day": 10, "price": 200}, ...]
    discount_info: List[DiscountInfo] = []
    allow_coupon: bool = True


class QStrategyUpdateIn(CustomBaseModel):
    product_id: str  # id is required
    changed: QStrategyUpdateFields

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "product_id": 0,
                "changed": {
                    "name": "goot strategy",
                    "package_id": "pkg2",
                    "market_id": 2,
                    "tags": ["a", "b"],
                    "ideas": "什么也不知道",
                    "desc": "一个策略，改了描述",
                    "category": 2,
                    "style": "NewStyle",
                    "suit_money": 123345567,
                    "buyout_price": 1,
                    "limit_copy": 1,
                    "limit_interval": 20,
                    "view_cnt": 0,
                    "collect_cnt": 0,
                    "share_cnt": 0,
                    "total_cnt": 10,
                    "sell_cnt": 1,
                    "sell_cnt_show": 2,
                    "period_prices": [
                        {"day": 10, "gift_day": 10, "price": 200},
                        {"day": 20, "gift_day": 20, "price": 650},
                    ],
                    # 时段购买价格信息 [{name: abc, day: 10, gift_day: 10, price: 200}...]
                    "enable_discount": True,
                    # 折扣信息 [{"start_dt": xxx, "end_dt": xxx, "day": 10, "gift_day": 10, "price": 200}, ...]
                    "discount_info": [
                        {
                            "start_ts": 1234214,
                            "end_ts": 2143214124,
                            "price": 200,
                            "day": 10,
                            "gift_day": 10,
                        }
                    ],
                    "allow_coupon": True,
                },
            }
        }


class QStrategyStatusOp(CustomBaseModel):
    product_id: Union[str, List[str]]
    status: ListStatus

    class Config:
        schema_extra = {"example": {"product_id": ["uuid1", "uuid2", "uuid3"]}}


class BuyedQStrategyInfo(QStrategyInfo):
    order_id: Optional[int]
    total_cash: Optional[float]
    total_days: Optional[int]
    days: Optional[int]
    gift_days: Optional[int]
    coupon_days: Optional[int]
    coupon_cash: Optional[float]
    payed_cash: Optional[float]
    expire_dt: Optional[datetime.datetime]
    create_dt: Optional[datetime.datetime]
    pay_dt: Optional[datetime.datetime]

    # class Config:


class BuyedQStrategySearch(BaseSearch):
    product_id: Optional[UUID]
    status: Optional[OrderStatus]
    show_expired: Optional[bool] = False


class BuyedQStrategySearchOut(CommonOut):
    data: List[BuyedQStrategyInfo] = []


class QStrategySearch(BaseSearch):
    product_id: Optional[UUID]
    name: Optional[SearchStr]
    task_id: Optional[SearchStr]
    su_cash: Optional[SearchStr]
    to_cash: Optional[SearchStr]
    ye_cash: Optional[SearchStr]
    max_cash: Optional[SearchStr]
    chu_cash: Optional[SearchStr]
    market_id: Optional[int]
    package_id: Optional[SearchStr]
    style: Optional[SearchStr]
    tag: Optional[SearchStr]
    category: Optional[QStrategyType]
    status: Optional[ListStatus]
    sort : Optional[SearchStr]

    class Config:
        schema_extra = {
            "example": {
                "name": "",
                "market": -1,
                "task_id":' ',
                'su_cash':'su_cash',#累计收益
                'to_cash':'-to_cash',#今日收益
                'ye_cash':'-ye_cash',#年化收益
                'max_cash':'max_cash',#最大回测
                'chu_cash':'chu_cash',#初始资金
                "status": 1,
                "offset": 0,
                "count": 100,
                "sort":''
            }
        }


class QStrategySearchOut(CommonOut):
    data: List[QStrategyInfo] = []


class QStrategyOVInfo(QStrategyInfo, Indicators):
    curve: List[Tuple[int, float]]
    bench_curve: List[Tuple[int, float]]
    returns: Optional[float]
    daily_returns: Optional[float]
    bench_returns: Optional[float]
    daily_bench_returns: Optional[float]


class QStrategySearchOVOut(CommonOut):
    data: List[QStrategyOVInfo] = []


class QStrategyBasicInfo(CommonOut):
    """策略概览"""

    product_id: Optional[UUID]
    tags: List[str]
    max_drawdown_period: Optional[
        Union[Tuple[datetime.datetime, datetime.datetime], List]
    ]
    discount_info: List[DiscountInfo]
    period_prices: List[PriceInfo]
    name: Optional[str]
    style: Optional[str]
    category: QStrategyType
    author_name: Optional[str]
    ideas: Optional[str]
    desc: Optional[str]
    buyout_price: Optional[float]
    task_id: Optional[str]
    sell_cnt: Optional[int]
    total_cnt: Optional[int]
    sim_start_dt: Optional[datetime.datetime]
    online_dt: Optional[datetime.datetime]
    enable_discount: Optional[bool] = False
    allow_coupon: Optional[bool] = False
    cum_returns: Optional[float]
    annual_returns: Optional[float]
    cum_bench_returns: Optional[float]
    annual_bench_returns: Optional[float]
    alpha: Optional[float]
    beta: Optional[float]
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    daily_win_raito: Optional[float]
    day: Optional[float]
    win_ratio: Optional[float]
    pnl_ratio: Optional[float]
    retruns1m: Optional[float]
    retruns1m_bench: Optional[float]
    returns: Optional[float]
    daily_returns: Optional[float]
    bench_returns: Optional[float]
    daily_bench_returns: Optional[float]
    returns_1m: Optional[float]
    returns_3m: Optional[float]
    returns_6m: Optional[float]
    returns_12m: Optional[float]
