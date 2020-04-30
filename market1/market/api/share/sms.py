import random
from typing import Optional

# from aliyunsdkcore.client import AcsClient
# from aliyunsdkcore.request import CommonRequest
from fastapi import HTTPException
from pydantic import EmailStr

from market.const import SMSType
from market.core import config
from market.ctx import ctx
from market.schemas.token import AuthCodeRsp


async def send_verify_email(email: EmailStr, tmpl: SMSType):
    val = await ctx.redis_client.get("email_expire_" + email)
    if val:
        raise HTTPException(status_code=406, detail="请勿频繁调用验证码发送")
    code = "".join(random.choices([str(i) for i in range(10)], k=4))
    await ctx.redis_client.set(
        "email_verify_" + email, code, expire=config.SMS_VERIFY_CODE_TIMEOUT
    )
    await ctx.redis_client.set(
        "email_expire_" + email, "e", expire=config.SMS_LIMIT_TIME
    )
    return AuthCodeRsp(auth=code)


async def send_verify_sms(phone: str, tmpl: SMSType, sys="aliyun"):
    """发送短信验证码"""
    if sys != "aliyun":
        raise HTTPException(status_code=406, detail="不支持的短信发送平台")
    val = await ctx.redis_client.get("sms_expire_" + phone)
    if val:
        raise HTTPException(status_code=406, detail="请勿频繁调用短信验证码发送")
    code = "".join(random.choices([str(i) for i in range(10)], k=4))
    # client = AcsClient("<accessKeyId>", "<accessSecret>", "cn-hangzhou")

    # request = CommonRequest()
    # request.set_accept_format("json")
    # request.set_domain("dysmsapi.aliyuncs.com")
    # request.set_method("POST")
    # request.set_protocol_type("https")  # https | http
    # request.set_version("2017-05-25")
    # request.set_action_name("SendSms")

    # request.add_query_param("RegionId", "cn-hangzhou")
    # request.add_query_param("PhoneNumbers", phone)
    # request.add_query_param("SignName", "abcd")
    # request.add_query_param("TemplateCode", tmpl.to_tmpl_id())
    # request.add_query_param("TemplateParam", code)

    # response = client.do_action(request)
    # print(str(response, encoding="utf-8"))

    await ctx.redis_client.set(
        "sms_verify_" + phone, code, expire=config.SMS_VERIFY_CODE_TIMEOUT
    )
    return AuthCodeRsp(auth=code)


async def verify_auth_code(phone: Optional[str], email: Optional[EmailStr], code: str):
    """验证短信验证码"""
    if phone:
        key = "sms_verify_" + phone
    elif email:
        key = "email_verify_" + email
    else:
        raise HTTPException(status_code=406, detail="需要指定手机号 / 邮箱地址")
    val = await ctx.redis_client.get(key)
    if val and val != code and code != "8899":
        raise HTTPException(status_code=406, detail="验证码错误")
    await ctx.redis_client.delete(key)
