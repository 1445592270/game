import abc
import datetime
import re
from typing import Dict, List, Optional, Union

from fastapi import Query
from pydantic import UUID1, BaseModel, ValidationError, validator

from market.core import config

# from pydantic.json import timedelta_isoformat


order_by_patern = re.compile(r"\s|[^a-zA-Z0-9-]")


def uuid_encoder(obj):
    if isinstance(obj, UUID1):
        return obj.hex
    raise ValidationError("invalid uuid")


class CustomBaseModel(BaseModel, abc.ABC):
    class Config:
        json_encoders = {
            datetime.datetime: lambda v: v.strftime("%Y-%m-%d %H:%M:%S"),
            # timedelta: timedelta_isoformat,
        }


class CommonOut(CustomBaseModel):
    errCode: int = 0
    errMsg: str = "Ok"
    total: Optional[int] = 0
    data: Optional[Union[List, Dict, str]]


class BaseSearch(CustomBaseModel):
    fuzzy: Optional[str]  # 模糊搜索字符串
    order_bys: List[str] = []
    offset: int = Query(default=0, ge=0)
    count: int = Query(
        default=config.DEFAULT_PAGE_SIZE, gt=0, le=config.PAGE_SIZE_LIMIT
    )

    @validator("order_bys")
    @classmethod
    def check_invalid_chars(cls, v):
        for s in v:
            if order_by_patern.search(s):
                raise ValidationError("no speical char allowed")
        return v


class SearchStr(str):
    """
    搜索字符串，限制了长度
    """

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        # __modify_schema__ should mutate the dict it receives in place,
        # the returned value will be ignored
        field_schema.update(
            # simplified regex here for brevity, see the wikipedia link above
            pattern="^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$",
            # some example postcodes
            examples=["SP11 9DG", "w1j7bu"],
        )

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("string required")
        if len(v) > 64:
            raise ValueError("search string too long, max is 64")
        # you could also return a string here which would mean model.post_code
        # would be a string, pydantic won't care but you could end up with some
        # confusion since the value's type won't match the type annotation
        # exactly
        return v

    def __repr__(self):
        return f"SearchStr({super().__repr__()})"


class PasswordStr(str):
    """密码"""

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        # __modify_schema__ should mutate the dict it receives in place,
        # the returned value will be ignored
        field_schema.update(
            # simplified regex here for brevity, see the wikipedia link above
            pattern="^[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}$",
            # some example postcodes
            examples=["SP11 9DG", "w1j7bu"],
        )

    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("string required")
        if len(v) > 32:
            raise ValueError("password string too long, max is 32")
        if len(v) < 8:
            raise ValueError("password string too short, min is 8")
        count = 0
        has_upper = re.match(r".*[A-Z]+", v)
        has_lower = re.match(r".*[a-z]+", v)
        has_digit = re.match(r".*[0-9]+", v)
        has_symbol = re.match(r".*[\W]+", v)
        if has_upper:
            count += 1
        if has_lower:
            count += 1
        if has_digit:
            count += 1
        if has_symbol:
            count += 1
        if count < 2:
            raise ValueError("password must contains UPPER/lower/digit/symbol")
        # you could also return a string here which would mean model.post_code
        # would be a string, pydantic won't care but you could end up with some
        # confusion since the value's type won't match the type annotation
        # exactly
        return v

    def __repr__(self):
        return "PasswordStr(****)"
