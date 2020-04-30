from typing import Optional

from fastapi import Query
from pydantic import UUID1, EmailStr

from market.models.const import UserStatus
from market.schemas.base import CustomBaseModel, PasswordStr


class UserInfo(CustomBaseModel):
    id: int
    uuid: UUID1
    name: str
    phone: Optional[str]
    email: Optional[EmailStr]
    password: PasswordStr
    broker_id: Optional[str]
    status: UserStatus

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class UserCreate(CustomBaseModel):
    name: str = Query(..., min_length=5, max_length=32)
    phone: Optional[str] = Query(..., max_length=14)
    email: Optional[EmailStr]
    sms_code: str = Query(..., min_length=4, max_length=6)
    password: PasswordStr
    broker_id: Optional[str] = Query(..., max_length=32)  # 代理商 ID
    vcode_id: Optional[str]
    vcode: Optional[str]


class UserRsp(CustomBaseModel):
    id: int
    uuid: UUID1
    name: str
    phone: Optional[str]
    email: Optional[EmailStr]


# Properties to receive via API on update
class UserUpdate(CustomBaseModel):
    name: str = Query(..., min_length=5, max_length=32)
    scope: Optional[str]


class UserIn(CustomBaseModel):
    uid: str
    sms_code: Optional[str]
    password: Optional[str]
    vcode_id: Optional[str]
    vcode: Optional[str]


class ResetPassword(CustomBaseModel):
    email: Optional[EmailStr]
    phone: Optional[str]
    password: PasswordStr
    sms_code: str
    vcode_id: str
    vcode: str


class UpdatePassword(CustomBaseModel):
    old_pwd: str = Query(..., min_length=1, max_length=32)
    new_pwd: PasswordStr
