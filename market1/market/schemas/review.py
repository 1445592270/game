import datetime
from typing import List, Optional, Union
from uuid import UUID

from fastapi import Query

from market.models.const import ProductType, QStrategyType, ReviewOP, ReviewStatus
from market.schemas.base import BaseSearch, CommonOut, CustomBaseModel, SearchStr
from market.schemas.package import PriceInfo


class ApplyQuery(CustomBaseModel):
    """申请查询"""

    sim_id: Union[List[str], str]
    user_id: str = Query(..., min_length=1, max_length=32)


class ApplyQueryRet(CustomBaseModel):
    sim_id: int
    name: Optional[str]
    task_id: Optional[str]
    sell_cnt: Optional[int]
    total_cnt: Optional[int]
    review_dt: Optional[datetime.datetime]
    status: ReviewStatus
    msg: Optional[str]


class OnlineApplyInfo(CustomBaseModel):
    user_id: str = Query(..., min_length=1, max_length=32)
    sim_id: str = Query(..., min_length=1, max_length=32)
    market_id: Optional[int]
    name: str = Query(..., min_length=1, max_length=32)  # 策略名称
    category: QStrategyType = QStrategyType.stock  # 策略类型，1= 股票，2= 期货
    style: str = Query(default="", max_length=32)  # 策略风格
    tags: List[str] = []  # 标签数组
    suit_money: float = Query(..., ge=0)  # 适合资金
    buyout_price: float = Query(..., ge=0)  # 买断价格
    total_cnt: int = Query(..., gt=0)  # 总份数
    period_prices: Optional[List[PriceInfo]]
    allow_coupon: Optional[bool] = False  # 是否可使用优惠券

    contact: str
    ideas: Optional[str]  # 策略思路
    desc: Optional[str]  # 描述
    msg: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "user_id": "量化家用户手机号",
                "sim_id": "量化家模拟交易 id",
                "market_id": -1,
                "name": "策略名字",
                "category": 1,
                "style": "aa",
                "suit_money": 1000,
                "buyout_price": 10,
                "total_cnt": 1000,
            }
        }


class OfflineApplyInfo(CustomBaseModel):
    """下架申请"""

    sim_id: str
    user_id: str = Query(..., min_length=1, max_length=32)
    contact: str
    msg: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "sim_id": "量化家模拟交易 id",
                "user_id": "量化家用户手机号",
                "contact": "12312314",
            }
        }


class ReviewInfo(CustomBaseModel):
    id: int
    market_id: Optional[int]
    create_dt: datetime.datetime
    product_id: UUID
    product_type: ProductType  # 商品类型：1= 策略，2= 套餐，3=vip
    operation: ReviewOP  # 操作类型：1= 上架，2= 下架
    user_id: int  # 申请人
    contact: str = Query(default="", max_length=14)  # 申请人手机号
    # review op info
    review_status: Optional[ReviewStatus]  # 审核状态
    review_dt: Optional[datetime.datetime]
    review_msg: Optional[str] = Query(default="", max_length=1024)
    # strategy/pkg product
    name: Optional[str]  # sim/pkg name
    sim_name: Optional[str]
    task_id: Optional[str]
    bt_task_id: Optional[str]
    sim_start_dt: Optional[datetime.datetime]
    start_cash: Optional[float]
    category: Optional[QStrategyType]


class ReviewDel(CustomBaseModel):
    id: Union[int, List[int]]

    class Config:
        schema_extra = {"example": {"id": [1, 2, 3]}}


class ReviewSearch(BaseSearch):
    review_id: Optional[int]
    market_id: Optional[int]
    product_id: Optional[UUID]
    product_type: Optional[ProductType]  # 商品类型：1= 策略，2= 套餐，3=vip
    operation: Optional[ReviewOP]  # 操作类型：1= 上架，2= 下架
    review_status: Optional[ReviewStatus]  # 审核状态
    user_id: Optional[int]  # 申请人
    contact: Optional[SearchStr]  # 申请人手机号

    class Config:
        schema_extra = {"example": {"market_id": -1, "offset": 0, "count": 100}}


class ReviewResult(CustomBaseModel):
    id: int
    accept: bool
    msg: Optional[str]


class ReviewSearchOut(CommonOut):
    data: List[ReviewInfo]


class ApplyQueryOut(CommonOut):
    data: List[ApplyQueryRet]
