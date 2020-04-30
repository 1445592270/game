import logging
from uuid import UUID
from typing import List, Union

from fastapi import HTTPException, status
from fastapi.exceptions import ValidationError
from tortoise.exceptions import IntegrityError
from tortoise.query_utils import Q

from market.models.const import ListStatus
from market.models.package import StrategyPackage
from market.schemas.base import CommonOut
from market.schemas.package import PkgCreate, PkgSearch, PkgSearchOut, PkgUpdateFields

logger = logging.getLogger(__name__)


def uuid_encoder(obj):
    if isinstance(obj, UUID):
        return obj.hex
    raise ValidationError("invalid uuid")


async def show_pkg(pkg_id: str):
    """查看策略套餐"""
    pkg = await StrategyPackage.get(product_id=pkg_id)
    return pkg


async def create_package(schema_in: PkgCreate):
    """添加套餐"""
    try:
        await StrategyPackage.create(**schema_in.dict())
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="创建套餐失败，请检查名字是否重复"
        )
    except Exception:
        logger.exception("create tag failed: %s", schema_in.json())
        raise HTTPException(status_code=400, detail="数据库错误")

    return CommonOut()


async def edit_pkg(product_id, changed: PkgUpdateFields):
    """编辑套餐"""
    try:
        await StrategyPackage.filter(product_id=product_id).update(**changed.dict())
    except IntegrityError:
        raise HTTPException(status_code=400, detail="更新套餐失败，请检查名字是否重复")
    except Exception:
        logger.exception("更新套餐 (%s) 失败：%s", product_id, changed.json())
        raise HTTPException(status_code=400, detail="数据库错误")
    return CommonOut()


async def change_pkg_status(product_id: UUID, change_status: ListStatus):
    """更改套餐状态"""
    try:
        await StrategyPackage.filter(product_id=product_id).update(status=change_status)
    except Exception:
        logger.exception("更新套餐 (%s) 状态失败：%s", product_id, change_status)
        raise HTTPException(status_code=400, detail="数据库错误")
    return CommonOut()


async def search_pkg(schema_in: PkgSearch):
    """搜索套餐"""
    # TODO: support tag search, perphaps need to use raw sql
    # from tortoise import Tortoise
    # con = Tortoise.get_connection()
    # await con.execute()
    query = StrategyPackage.filter()
    if schema_in.status:
        query = query.filter(status=schema_in.status)
    else:
        query = query.filter(~Q(status=ListStatus.deleted))
    if schema_in.product_id:
        query = query.filter(product_id=schema_in.product_id)
    if schema_in.name:
        query = query.filter(name__contains=schema_in.name)
    if schema_in.tag:
        # TODO: support tag search
        pass
    if schema_in.market_id:
        query = query.filter(market__id=schema_in.market_id)
    total_count = await query.count()
    pkg_list = (
        await query.order_by("name").offset(schema_in.offset).limit(schema_in.count)
    )
    # tag_names = [tag.name for tag in tags]
    return PkgSearchOut(total=total_count, data=[pkg for pkg in pkg_list],)
