import logging
import uuid

from fastapi import APIRouter, Depends
from tortoise.exceptions import IntegrityError

from market.api.share.package import change_pkg_status, edit_pkg, search_pkg, show_pkg
from market.core.security import require_super_scope_admin, require_super_scope_su
from market.models.admin_user import MarketAdminUser
from market.models.package import StrategyPackage
from market.schemas.base import CommonOut
from market.schemas.package import (
    PkgInfo,
    PkgCreate,
    PkgSearch,
    PkgSearchOut,
    PkgStatusOp,
    PkgUpdateIn,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/pkg/new", response_model=CommonOut, tags=["后台——套餐管理"])
async def add_package(
    schema_in: PkgCreate,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """添加套餐"""
    schema_in.product_id = uuid.uuid1()
    try:
        await StrategyPackage.create(**schema_in.dict())
    except IntegrityError:
        return CommonOut(errCode=-1, errMsg="添加失败，请检查名字是否重复")
    except Exception:
        logger.exception("create package failed: %s", schema_in.json())
        return CommonOut(errCode=-1, errMsg="添加失败，请检查名字是否重复")

    return CommonOut()


@router.post("/pkg/edit", response_model=CommonOut, tags=["后台——套餐管理"])
async def admin_edit_pkg(
    schema_in: PkgUpdateIn,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """编辑套餐"""
    return await edit_pkg(schema_in.product_id, schema_in.changed)


@router.post("/pkg/status/change", response_model=CommonOut, tags=["后台——套餐管理"])
async def change_status(
    schema_in: PkgStatusOp,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """下架套餐"""
    return await change_pkg_status(schema_in.product_id, schema_in.status)


@router.post("/pkg/find", response_model=PkgSearchOut, tags=["后台——套餐管理"])
async def admin_search_pkg(
    schema_in: PkgSearch,
    current_user: MarketAdminUser = Depends(require_super_scope_admin),
):
    """搜索套餐"""
    return await search_pkg(schema_in)


@router.get("/pkg/{pkg_id}", response_model=PkgInfo, tags=["后台——套餐管理"])
async def admin_show_pkg(
    pkg_id: str, current_user: MarketAdminUser = Depends(require_super_scope_su),
):
    """查看策略套餐"""
    return await show_pkg(pkg_id)
