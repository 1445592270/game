from typing import List, Optional, Union
from uuid import UUID

from fastapi import Query

from market.models.const import PushMethod, PushStatus
from market.schemas.base import BaseSearch, CommonOut, CustomBaseModel, SearchStr


class PushCreate(CustomBaseModel):
    qstrategy_id: UUID
    push_method: PushMethod = PushMethod.wechat
    push_id: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "qstrategy_id": "uuid1",
                "push_method": 1,
                "push_id": "wechat_id",
            }
        }


class PushSearchIn(BaseSearch):
    qstrategy_id: Optional[SearchStr]
    task_id: Optional[SearchStr]
    push_method: Optional[PushMethod]

    class Config:
        schema_extra = {"example": {"qstrategy_id": "xxx", "task_id": "xxx"}}
