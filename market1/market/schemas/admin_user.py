import datetime
from typing import List, Optional
from uuid import UUID

from fastapi import Query
from pydantic import EmailStr

from market.models.const import SUPER_SCOPE, UserScope2, UserStatus
from market.schemas.base import BaseSearch, CommonOut, CustomBaseModel, PasswordStr


# Shared properties
class AdminUserInfo(CustomBaseModel):
    id: int
    uuid: UUID
    name: str
    phone: Optional[str]
    email: Optional[EmailStr]
    scope1: str
    scope2: UserScope2
    status: UserStatus
    create_dt: Optional[datetime.datetime]

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class AdminUserCreate(CustomBaseModel):
    name: str = Query(..., min_length=5, max_length=32)
    phone: str = Query(..., min_length=11, max_length=14)
    email: EmailStr
    password: str
    scope1: str = SUPER_SCOPE
    scope2: UserScope2 = UserScope2.su


# Properties to receive via API on update
class AdminUserUpdateField(CustomBaseModel):
    name: str = Query(..., min_length=5, max_length=32)
    password: str
    scope: str


class AdminUserUpdate(CustomBaseModel):
    id: int
    changed: AdminUserUpdateField


class AdminUserChangeStatusIn(CustomBaseModel):
    id: int
    status: UserStatus


class AdminUserIn(CustomBaseModel):
    user_id: str
    password: PasswordStr
    verification_code: str


# class Token(CustomBaseModel):
#     access_token: Optional[str]
#     token_type: Optional[str]


class AdminUserSearchIn(BaseSearch):
    name: Optional[str]
    phone: Optional[str]
    email: Optional[str]
    scope1: Optional[str]
    scope2: Optional[UserScope2]


class AdminUserSearchOut(CommonOut):
    data: List[AdminUserInfo] = []
