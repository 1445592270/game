import datetime
import logging
from typing import List, Union
from uuid import UUID

from starlette.requests import Request
from tortoise.query_utils import Q

from market.const import TaskType
from market.core.security import api_key_schema, get_active_user
from market.models.const import ListStatus, OrderStatus, ProductType
from market.models.order import UserOrder
from market.models.strategy import QStrategy
from market.models.user import MarketUser
from market.schemas.base import CommonOut
from market.schemas.strategy import (
    QStrategyInfo,
    QStrategySearch,
    QStrategySearchOut,
    QStrategyUpdateFields,
)

logger = logging.getLogger(__name__)


async def check_task_permission(task_type: TaskType, task_id: str, request: Request):
    """检查用户是否有该策略的权限"""
    try:
        current_user: MarketUser = await get_active_user(request)
    except Exception:
        logger.warning("check_task_permission no active user found")
        return False
    if task_type == TaskType.PAPER_TRADING:
        product = await QStrategy.get_or_none(task_id=task_id)
        #print(product,'121212121212')
        #print(product.market_id,'market_id333333333333')
        #print(product.package_id,'product.package_id222222222222222')
    else:
        product = await QStrategy.get_or_none(bt_task_id=task_id)
        #print(product,'222222222222222222222211111111111')
    if not product:
        #print(3333333333333333333333333333)
        logger.warning("check_task_permission no product found")
        return False
    user_order = await UserOrder.filter(
        user__id=current_user.id,
        product_type=ProductType.qstrategy,
        #product_id=product.product_id,
        status=OrderStatus.payed,
        expire_dt__gt=datetime.datetime.now(),
    )
    #print(current_user.id)
    #print(11)
    #print(user_order.id)
    #print(Product)
    #print(product.product_id)
    #print(3333333)
    #print(OrderStatus.payed)
    #print(222)
    #print(user_order)
    if user_order:
       # print(111111111111111)
        logger.warning("check_task_permission no user order found")
        return True
    return False


async def show_strategy(strategy_id: UUID):
    """查看策略"""
    strategy = await QStrategy.get_or_none(product_id=strategy_id)
    if not strategy:
        return CommonOut(errCode=-1, errMsg="没找到该策略")
    return QStrategyInfo(**strategy.__dict__)


async def edit_strategy(product_id: str, changed: QStrategyUpdateFields):
    """编辑上架策略"""
    try:
        await QStrategy.filter(product_id=product_id).update(**changed.dict())
    except Exception:
        logger.exception("更新策略 (%s) 失败：%s", product_id, changed.json())
        return CommonOut(errCode=-1, errMsg="更新失败，请检查名字是否重复")
    return CommonOut()


async def change_strategy_status(id_list: Union[str, List[str]], status: ListStatus):
    """直接重新上架策略"""
    if isinstance(id_list, str):
        id_list = [id_list]
    await QStrategy.filter(product_id__in=id_list).update(status=status)
    return CommonOut()


async def search_strategy(schema_in: QStrategySearch, return_strategy_list=False):
    """搜索策略"""
    # TODO: support tag search, perphaps need to use raw sql
    # from tortoise import Tortoise
    # con = Tortoise.get_connection()
    # await con.execute()
    query = QStrategy.filter()
    if schema_in.status:
        query = query.filter(status=schema_in.status)
    else:
        query = query.filter(status=ListStatus.online)
        #print(query)

    if schema_in.product_id:
        query = query.filter(product_id=schema_in.product_id)
    if schema_in.market_id:
        query = query.filter(market__id=schema_in.market_id)
    if schema_in.package_id:
        query = query.filter(package__id=schema_in.package_id)
    if schema_in.task_id:
        query = query.filter(task_id__contains=schema_in.task_id)
    if schema_in.style:
        query = query.filter(style__contains=schema_in.style)
    if schema_in.category:
        query = query.filter(category__contains=schema_in.category)
    if schema_in.name:
        query = query.filter(name__contains=schema_in.name)
    total_count = await query.count()
    strategy_list = (
        await query.order_by("name").offset(schema_in.offset).limit(schema_in.count)
    )
    if return_strategy_list:
       # print(3333333333333333333333333333333333333)
        return total_count, strategy_list
    # tag_names = [tag.name for tag in tags]
    #print(44444444444444444444444444444444444444444444)
    return QStrategySearchOut(
        total=total_count, data=[strategy for strategy in strategy_list],
    )


async def search_strategy1(schema_in: QStrategySearch, return_strategy_list=False):
    query = QStrategy.filter()
    if schema_in.status:
        query = query.filter(status=schema_in.status)
    else:
        query = query.filter(status=ListStatus.online)
        #print(query,'111111111111111111111111111111111111111111111111111111111111111111')
    if schema_in.product_id:
        query = query.filter(product_id=schema_in.product_id)
    if schema_in.market_id:
        query = query.filter(market__id=schema_in.market_id)
    if schema_in.package_id:
        query = query.filter(package__id=schema_in.package_id)
    if schema_in.task_id:
        query = query.filter(task_id__contains=schema_in.task_id)
    if schema_in.style:
        query = query.filter(style__contains=schema_in.style)
    if schema_in.category:
        query = query.filter(category__contains=schema_in.category)
    if schema_in.name:
        query = query.filter(name__contains=schema_in.name)
    #if schema_in.package_id and schema_in.style:
    #    query = query.filter(package__id=schema_in.package_id,style__contains=schema_in.style)
    #strategy_list = await query.order_by("name").offset(schema_in.offset).limit(schema_in.count)
    strategy_list = await query.order_by("name")
    if return_strategy_list:
        return  strategy_list
    return QStrategySearchOut(
            data=[strategy for strategy in strategy_list],
            )
