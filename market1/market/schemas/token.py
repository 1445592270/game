from typing import Optional

from pydantic import UUID1, EmailStr

from market.schemas.base import CommonOut, CustomBaseModel


class AuthCodeRsp(CommonOut):
    auth: str


class AdminToken(CustomBaseModel):
    """
    超级超级管理员

        scope1: aq
        scope2: 1

    scope1: 标识管理员管理的超市，aq 为特殊类型，可管理所有的超市

    scope2: 标识管理员的权限划分，1 为超管，具有所有的权限
    """

    id: int
    uuid: UUID1
    name: str
    phone: Optional[str]
    email: Optional[EmailStr]
    scope1: str
    scope2: int
    token: str


class UserToken(CustomBaseModel):
    id: int
    uuid: UUID1
    name: str
    phone: Optional[str]
    email: Optional[EmailStr]
    broker_id: Optional[str]
    token: str
