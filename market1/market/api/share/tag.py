import logging

from fastapi import HTTPException
from tortoise.exceptions import IntegrityError

from market.models.tag import Tag
from market.schemas.base import CommonOut
from market.schemas.tag import TagBatDel, TagCreate, TagSearch, TagSearchOut, TagUpdate

logger = logging.getLogger(__name__)


async def add_tag(schema_in: TagCreate):
    """添加标签或者风格"""
    name_list = schema_in.name
    if isinstance(name_list, str):
        name_list = [name_list]

    # for name in name_list:
    # await Tag.create(name=name, tag_type=schema_in.tag_type)
    try:
        await Tag.bulk_create(
            [Tag(name=name, tag_type=schema_in.tag_type) for name in name_list]
        )
    except IntegrityError:
        raise HTTPException(status_code=400, detail="创建标签 / 风格失败，请检查名字是否重复")
    except Exception:
        logger.exception("create tag failed: %s", schema_in.json())
        raise HTTPException(status_code=400, detail="数据库错误")

    return CommonOut()


async def edit_tag(schema_in: TagUpdate):
    """编辑标签或者风格的名字"""
    try:
        await Tag.filter(id=schema_in.id).update(name=schema_in.name)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="更新标签 / 风格失败，请检查名字是否重复")
    except Exception:
        logger.exception("create tag failed: %s", schema_in.json())
        raise HTTPException(status_code=400, detail="数据库错误")
    return CommonOut()


async def del_tag(schema_in: TagBatDel):
    """删除标签或风格，可传单个 id 或者 id 列表"""
    id_list = schema_in.id
    if isinstance(id_list, int):
        id_list = [id_list]
    await Tag.filter(id__in=id_list).update(deleted=True)
    return CommonOut()


async def search_tag(schema_in: TagSearch):
    """根据名字和类型查询标签或者风格"""
    query = Tag.filter(deleted=False)
    if schema_in.tag_type:
        query = query.filter(tag_type=schema_in.tag_type)
    if schema_in.name:
        query = query.filter(name__contains=schema_in.name)
    total_count = await query.count()
    tags = await query.order_by("name").offset(schema_in.offset).limit(schema_in.count)
    return TagSearchOut(total=total_count, data=[tag for tag in tags])


async def show_tag(tag_id: int):
    """查看标签或者风格"""
    return await Tag.get(id=tag_id)
