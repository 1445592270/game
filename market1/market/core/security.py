import datetime
import logging
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyCookie, APIKeyHeader
from passlib.context import CryptContext
from starlette.requests import Request
from tortoise.exceptions import DoesNotExist

from market.models.admin_user import MarketAdminUser
from market.models.const import SUPER_SCOPE, UserScope2, UserStatus
from market.models.user import MarketUser

logger = logging.getLogger(__name__)
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

APIKEY_HEADER_NAME = "X-API-KEY"
# api_key_schema = APIKeyCookie(name=APIKEY_HEADER_NAME)
api_key_schema = APIKeyHeader(name=APIKEY_HEADER_NAME)


def verify_password(plain_password, hashed_password, salt: str):
    logger.info(
        "plain: %s, hash: %s new hash: %s",
        plain_password,
        hashed_password,
        pwd_context.hash("#".join((salt, plain_password))),
    )
    return pwd_context.verify("#".join((salt, plain_password)), hashed_password)


def get_password_hash(password, salt):
    return pwd_context.hash("#".join((salt, password)))


def create_access_token(*, data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now() + expires_delta
    else:
        expire = datetime.datetime.now() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt.decode("utf-8")


# -----
async def authenticate_user(user_id: str, password: str):
    try:
        user = await MarketUser.get(phone=user_id)
    except DoesNotExist:
        try:
            user = await MarketUser.get(email=user_id)
        except DoesNotExist:
            try:
                user = await MarketUser.get(phone=user_id)
            except DoesNotExist:
                return False
    if not verify_password(password, user.password, user.uuid.hex):
        return False
    return user


async def get_user(user_uuid: UUID):
    try:
        return await MarketUser.get(uuid=user_uuid)
    except DoesNotExist:
        return None


async def require_user(token: str = Depends(api_key_schema)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uuid_hex = payload.get("uuid")
        if not uuid_hex:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={APIKEY_HEADER_NAME: ALGORITHM},
            )
        expire = payload.get("exp")
        if not expire or datetime.datetime.now().timestamp() > float(expire):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="credentials expired",
                headers={APIKEY_HEADER_NAME: ALGORITHM},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={APIKEY_HEADER_NAME: ALGORITHM},
        )
    user = await get_user(UUID(hex=uuid_hex))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={APIKEY_HEADER_NAME: ALGORITHM},
        )
    return user


async def require_active_user(current_user: MarketUser = Depends(require_user)):
    if current_user.status != UserStatus.normal:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_active_user(request: Request) -> MarketUser:
    """获取当前登录用户信息，获取失败时异常"""
    token = await api_key_schema(request)
    logging.warning(token)
    user = await require_user(token)
    logging.warning(user)
    #print("user:::",user)
    print("user_id::",user.id)
    print("user_name::",user.name)
    #print("user_status:::",user.status)
    return await require_active_user(await require_user(await api_key_schema(request)))


# -------------------------------------
async def authenticate_admin_user(user_id: str, password: str):
    try:
        user = await MarketAdminUser.get(phone=user_id)
    except DoesNotExist:
        try:
            user = await MarketAdminUser.get(email=user_id)
        except DoesNotExist:
            try:
                user = await MarketAdminUser.get(name=user_id)
            except DoesNotExist:
                return False
    if not verify_password(password, user.password, user.uuid.hex):
        return False
    return user


async def get_admin_user(user_uuid: UUID):
    try:
        return await MarketAdminUser.get(uuid=user_uuid)
    except DoesNotExist:
        return None


async def require_admin(token: str = Depends(api_key_schema)):
    """管理员"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={APIKEY_HEADER_NAME: ALGORITHM},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uuid_hex = payload.get("uuid")
        if not uuid_hex:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    user = await get_admin_user(user_uuid=UUID(hex=uuid_hex))
    if not user:
        raise credentials_exception
    return user


async def require_active_admin(current_user: MarketAdminUser = Depends(require_admin)):
    """激活状态的管理员"""
    if current_user.status != UserStatus.normal:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def require_super_scope_admin(
    current_user: MarketAdminUser = Depends(require_active_admin),
):
    """总后台的管理员"""
    if current_user.scope1 != SUPER_SCOPE:
        raise HTTPException(status_code=400, detail="Insufficient permissions")
    return current_user


async def require_super_scope_su(
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """总后台的超管"""
    if current_user.scope2 != UserScope2.su:
        raise HTTPException(status_code=400, detail="Insufficient permissions")
    return current_user
