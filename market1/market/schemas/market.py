from typing import List, Optional, Union

from fastapi import Query

from market.models.const import MarketStatus
from market.schemas.base import BaseSearch, CommonOut, CustomBaseModel, SearchStr


class MarketInfo(CustomBaseModel):
    id: int
    name: str = Query(..., min_length=4, max_length=64)
    domain: str = Query(..., min_length=4, max_length=128)
    # status = fields.IntEnumField(MarketStatus, default=1)  # 超市状态：1= 运行， 2= 停止

    class Config:
        orm_mode = True


class MarketCreate(CustomBaseModel):
    name: str = Query(..., min_length=4, max_length=64)
    domain: str = Query(..., min_length=4, max_length=128)
    # status = fields.IntEnumField(MarketStatus, default=1)  # 超市状态：1= 运行， 2= 停止

    class Config:
        schema_extra = {"example": {"name": "zzz", "domain": "http://www.baidu.com"}}


class MarketUpdate(CustomBaseModel):
    id: int
    name: Optional[str] = Query(..., min_length=4, max_length=64)
    domain: Optional[str] = Query(..., min_length=4, max_length=128)

    class Config:
        schema_extra = {
            "example": {"id": 123, "name": "yyy", "domain": "http://www.qq.com"}
        }


class MarketDisable(CustomBaseModel):
    id: Union[int, List[int]]
    status: MarketStatus = MarketStatus.disabled

    class Config:
        schema_extra = {"example": {"id": [1, 2, 3]}}


class MarketSearch(BaseSearch):
    id: Optional[int]
    name: Optional[SearchStr]

    class Config:
        schema_extra = {"example": {"id": 1, "name": "zzz", "offset": 0, "count": 100}}


class MarketSearchOut(CommonOut):
    data: List[MarketInfo] = []
