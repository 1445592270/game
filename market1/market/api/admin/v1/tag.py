import logging

from fastapi import APIRouter, Depends

from market.api.share.tag import add_tag, del_tag, edit_tag, search_tag, show_tag
from market.core.security import require_super_scope_admin
from market.models.admin_user import MarketAdminUser
from market.schemas.base import CommonOut
from market.schemas.tag import (
    TagBatDel,
    TagCreate,
    TagInfo,
    TagSearch,
    TagSearchOut,
    TagUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/tag/new", response_model=CommonOut, tags=["后台——风格标签管理"])
async def admin_add_tag(
    schema_in: TagCreate,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """添加标签或者风格"""
    return await add_tag(schema_in)


@router.post("/tag/edit", response_model=CommonOut, tags=["后台——风格标签管理"])
async def admin_edit_tag(
    schema_in: TagUpdate,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """编辑标签或者风格的名字"""
    return await edit_tag(schema_in)


@router.post("/tag/del", response_model=CommonOut, tags=["后台——风格标签管理"])
async def admin_del_tag(
    schema_in: TagBatDel,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """删除标签或风格，可传单个 id 或者 id 列表"""
    return await del_tag(schema_in)


@router.post("/tag/find", response_model=TagSearchOut, tags=["后台——风格标签管理"])
async def admin_search_tag(
    schema_in: TagSearch,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """根据名字和类型查询标签或者风格"""
    return await search_tag(schema_in)


@router.get("/tag/{tag_id}", response_model=TagInfo, tags=["后台——风格标签管理"])
async def admin_show_tag(
    tag_id: int, current_user: MarketAdminUser = Depends(require_super_scope_admin)
):
    """查看标签或者风格"""
    return await show_tag(tag_id)
