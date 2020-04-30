import datetime
from typing import List, Optional, Union

from fastapi import Query
from pydantic import UUID1

from market.models.const import ListStatus
from market.schemas.base import BaseSearch, CommonOut, CustomBaseModel, SearchStr


class PriceInfo(CustomBaseModel):
    day: int = Query(..., gt=0)
    gift_day: int = Query(..., ge=0)
    price: float = Query(..., ge=0)

    class Config:
        orm_mode = True


class DiscountInfo(CustomBaseModel):
    start_ts: float = Query(..., ge=0)  # 毫秒时间戳
    end_ts: float = Query(..., gt=0)  # 毫秒时间戳
    day: int = Query(..., ge=0)
    price: float = Query(..., ge=0)

    class Config:
        orm_mode = True


class PkgInfo(CustomBaseModel):
    product_id: Optional[UUID1]
    name: str = Query(default="", min_length=1, max_length=64)
    market_id: int = 0
    market_name: str = ""
    tags: List[str] = []
    desc: str = ""
    status: ListStatus = ListStatus.online

    limit_copy: int = -1
    limit_interval: int = -1
    view_cnt: int = 0
    collect_cnt: int = 0
    share_cnt: int = 0

    buyout_price: int = 0
    # 时段购买价格信息 [{"day": 20, "gift_day": 20, "price": 350}, ...]
    period_prices: List[PriceInfo]
    enable_discount: bool = False
    # 折扣信息 [{"start_dt": xxx, "end_dt": xxx, "day": 10, "gift_day": 10, "price": 200}, ...]
    discount_info: List[DiscountInfo] = []
    allow_coupon: bool = True

    class Config:
        orm_mode = True


class PkgCreate(PkgInfo):
    market_id: int

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "pkg1",
                "market_id": 1,
                "tags": ["a", "b"],
                "desc": "一个套餐",
                "status": 1,
                "limit_copy": 1,
                "limit_interval": 20,
                "view_cnt": 0,
                "collect_cnt": 0,
                "share_cnt": 0,
                "period_prices": [
                    {"day": 10, "gift_day": 10, "price": 200},
                    {"day": 20, "gift_day": 20, "price": 350},
                ],
                "buyout_price": 10.3,
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


class PkgUpdateFields(CustomBaseModel):
    name: str = Query(default="", min_length=1, max_length=64)
    market_id: int
    tags: List[str] = []
    desc: str = ""
    status: ListStatus = ListStatus.offline

    limit_copy: int = -1
    limit_interval: int = -1
    view_cnt: int = 0
    collect_cnt: int = 0
    share_cnt: int = 0

    buyout_price: int = 0
    # 时段购买价格信息 [{"day": 20, "gift_day": 20, "price": 350}, ...]
    period_prices: List[PriceInfo]
    enable_discount: bool = False
    # 折扣信息 [{"start_dt": xxx, "end_dt": xxx, "day": 10, "gift_day": 10, "price": 200}, ...]
    discount_info: List[DiscountInfo] = []
    allow_coupon: bool = True


class PkgUpdateIn(CustomBaseModel):
    product_id: str  # id is required
    changed: PkgUpdateFields

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "product_id": "uuid1",
                "changed": {
                    "name": "pkg1_new",
                    "market_id": 2,
                    "tags": ["a", "b"],
                    "desc": "一个套餐，改了描述",
                    "status": 1,
                    "limit_copy": 1,
                    "limit_interval": 20,
                    "view_cnt": 0,
                    "collect_cnt": 0,
                    "share_cnt": 0,
                    "buyout_price": 11.3,
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


class PkgStatusOp(CustomBaseModel):
    # product_id: Union[UUID1, List[UUID1]]
    product_id: UUID1
    status: ListStatus

    class Config:
        schema_extra = {"example": {"product_id": ["uuid1", "uuid2"]}}


class PkgSearch(BaseSearch):
    product_id: Optional[SearchStr]
    name: Optional[SearchStr]
    tag: Optional[SearchStr]
    market_id: Optional[int]
    status: Optional[ListStatus]

    class Config:
        schema_extra = {
            "example": {
                "product_id": "",
                "name": "",
                "market_id": -1,
                "status": 1,
                "offset": 0,
                "count": 100,
            }
        }


class BuyedPkgSearch(BaseSearch):
    show_payed: Optional[bool] = True
    show_expired: Optional[bool] = False


class PkgSearchOut(CommonOut):
    data: List[PkgInfo] = []


class BuyedPkgInfo(PkgInfo):
    total_cash: float
    total_days: int
    days: int
    gift_days: int
    coupon_days: int
    coupon_cash: float
    create_dt: datetime.datetime
    payed_cash: Optional[float]
    pay_dt: Optional[datetime.datetime]
    expire_dt: Optional[datetime.datetime]


class BuyedPkgSearchOut(CommonOut):
    data: List[BuyedPkgInfo] = []
