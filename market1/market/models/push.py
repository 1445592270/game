from tortoise import fields

from market.models.base import Base
from market.models.const import PushMethod, PushStatus


class PushInfo(Base):
    """推送信息维护"""

    id = fields.IntField(pk=True)
    qstrategy_id = fields.UUIDField()
    task_id = fields.CharField(max_length=32, index=True)
    user_id = fields.IntField()  # 申请人
    # contact = fields.CharField(max_length=14)  # 申请人手机号
    status = fields.IntEnumField(PushStatus)  # 推送状态：1= 推送，2= 停用，2= 权限过期
    push_method = fields.IntEnumField(PushMethod, default=1)  # 推送类型
    push_id = fields.CharField(max_length=128)  # 推送 id，微信号 / 邮箱地址 /post 地址等
    create_dt = fields.DatetimeField(auto_now_add=True)  # 创建时间
    update_dt = fields.DatetimeField(auto_now=True)
