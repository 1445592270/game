from typing import List, Optional, Union

from pydantic import HttpUrl

from market.models.const import ProductType
from market.schemas.base import BaseSearch, CommonOut, CustomBaseModel, SearchStr


class CollectInfo(CustomBaseModel):
    id: int
    url: str
    product_id: str
    product_type: ProductType  # 商品类型：1= 策略，2= 套餐，3=vip
    # user_id: int
    # canceled = fields.BooleanField(default=False)  # 收藏状态：1= 正常，2= 取消收藏


class CollectCreate(CustomBaseModel):
    url: str
    product_id: str
    # 商品类型：1= 策略，2= 套餐，3=vip
    product_type: ProductType = ProductType.qstrategy

    class Config:
        schema_extra = {"example": {"url": "https://www.baidu.com"}}


class CollectDel(CustomBaseModel):
    id: Union[int, List[int]]

    class Config:
        schema_extra = {"example": {"id": [1, 2, 3]}}


class CollectSearch(BaseSearch):
    url: Optional[HttpUrl]
    product_id: Optional[SearchStr]
    # 商品类型：1= 策略，2= 套餐，3=vip
    product_type: Optional[ProductType]

    class Config:
        schema_extra = {"example": {"url": "baidu", "product_type": 1}}


class CollectSearchOut(CommonOut):
    data: List[CollectInfo] = []
