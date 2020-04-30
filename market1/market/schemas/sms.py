from typing import List, Optional, Union

from pydantic import EmailStr

from market.const import SMSType
from market.schemas.base import CustomBaseModel


class SMSIn(CustomBaseModel):
    smstype: SMSType
    phone: str


class EmailIn(CustomBaseModel):
    smstype: SMSType
    email: EmailStr
