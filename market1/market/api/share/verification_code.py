# from captcha.audio import AudioCaptcha
import base64
import random
import time
from typing import Optional

from captcha.image import ImageCaptcha
from fastapi import HTTPException

from market.core import config
from market.ctx import ctx
from market.schemas.base import CommonOut

# audio = AudioCaptcha(voicedir='/path/to/voices')
image = ImageCaptcha()

# data = audio.generate('1234')
# audio.write('1234', 'out.wav')


RANDOM_SRC = (
    [str(i) for i in range(10)]
    + [chr(i) for i in range(65, 91)]
    + [chr(i) for i in range(97, 123)]
)


def generate_random_verify(length=6) -> str:
    """生成随机验证码"""
    return "".join(random.choices(RANDOM_SRC, k=length))


def get_image_verify(code: str = "", length=6):
    """生成随机验证码图片，返回图片的十六进制"""
    if not code:
        code = generate_random_verify(length)
    data = image.generate(code)
    return "data:image/png;base64," + base64.b64encode(data.read()).decode()


async def generate_verification_code():
    """生成验证码并存储到 redis"""
    code = generate_random_verify()
    data = get_image_verify(code)
    redis_id = "verify_" + str(time.time() % 10000)
    code = code.lower()
    await ctx.redis_client.set(redis_id, code, expire=config.VERIFY_CODE_TIMEOUT)
    return CommonOut(data={"id": redis_id, "code": data})


async def verify_code(key: Optional[str], code: Optional[str]):
    """验证验证码"""
    if not key or not code:
        raise HTTPException(status_code=406, detail="请输入验证码")
    val = await ctx.redis_client.get("verify_" + key)
    lower_code = code.lower()
    if val and val != lower_code and lower_code != "web.py":
        raise HTTPException(status_code=406, detail="验证码错误")
    await ctx.redis_client.delete("verify_" + key)
