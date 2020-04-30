from typing import List, Optional, Union

from fastapi import Query

from market.models.const import TagType
from market.schemas.base import BaseSearch, CommonOut, CustomBaseModel, SearchStr


class TagInfo(CustomBaseModel):
    id: int
    name: str
    tag_type: int

    class Config:
        orm_mode = True


class TagCreate(CustomBaseModel):
    name: Union[str, List[str]] = Query(default="", min_length=1, max_length=32)
    tag_type: TagType = TagType.tag

    class Config:
        schema_extra = {"example": {"name": ["tag1", "tag2"], "tag_type": 1}}


class TagUpdate(CustomBaseModel):
    id: int
    name: str = Query(default="", min_length=1, max_length=32)

    class Config:
        schema_extra = {"example": {"id": 1, "name": "changed_name"}}


class TagBatDel(CustomBaseModel):
    id: Union[int, List[int]]

    class Config:
        schema_extra = {"example": {"id": [1, 2, 3]}}


class TagSearch(BaseSearch):
    name: Optional[SearchStr]
    tag_type: Optional[TagType] = TagType.tag  # <=0 means no filter by status

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {"search": "tag", "tag_type": 1, "offset": 0, "count": 100}
        }


class TagSearchOut(CommonOut):
    data: List[TagInfo] = []
