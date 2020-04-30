import logging

from tortoise.query_utils import Q

from market.models.const import OrderStatus
from market.models.order import UserOrder
from market.models.user import MarketUser
from market.schemas.order import OrderInfo, OrderSearch, OrderSearchOut

logger = logging.getLogger(__name__)


async def show_order(order_id: int):
    """查看订单详情"""
    order = UserOrder.get_or_none(id=order_id)
    if order:
        return OrderInfo(**order.__dict__)
    return None


async def search_order(schema_in: OrderSearch):
    """搜索用户的订单列表"""
    query = UserOrder.filter(~Q(status=OrderStatus.deleted))
    if schema_in.fuzzy:  # 订单模糊搜索，账户和订单 ID
        users = await MarketUser.filter(
            Q(phone__contains=schema_in.fuzzy)
            | Q(email__contains=schema_in.fuzzy)
            | Q(email__contains=schema_in.fuzzy),
        )
        user_ids = [user.id for user in users]
        query = UserOrder.filter(user_id__in=user_ids)
        try:
            order_id = int(schema_in.fuzzy)
            query = UserOrder.filter(id=order_id)
        except ValueError:
            pass
    if schema_in.order_id:
        query = UserOrder.filter(id=schema_in.order_id)
    if schema_in.user_id:
        query = UserOrder.filter(user_id=schema_in.user_id)
    if schema_in.product_id:
        query = UserOrder.filter(product_id=schema_in.product_id)
    if schema_in.product_type:
        query = UserOrder.filter(product_id=schema_in.product_type)
    if schema_in.status:
        query = UserOrder.filter(status=schema_in.status)

    total_count = await query.count()
    orders = (
        await query.order_by("id")
        .offset(schema_in.offset)
        .limit(schema_in.count)
        .prefetch_related("user")
    )
    data = []
    for order in orders:
        if order.user:
            info = {
                "user_id": order.user.id,
                "user_name": order.user.name,
                "user_phone": order.user.phone,
            }
        else:
            info = {"user_id": -1, "user_name": "deleted", "user_phone": "100000000000"}
        info.update(order.__dict__)
        data.append(info)
    return OrderSearchOut(total=total_count, data=data)
