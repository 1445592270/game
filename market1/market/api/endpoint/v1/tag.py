import logging

from fastapi import APIRouter  # , Depends

from market.api.share.tag import search_tag
from market.schemas.tag import TagSearch, TagSearchOut

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/tag/find", response_model=TagSearchOut, tags=["用户端——风格和标签页"])
async def user_search_tag(
    schema_in: TagSearch,  # , current_user: MarketUser = Depends(require_active_user)
):
    """根据名字和类型查询标签或者风格"""
    return await search_tag(schema_in)
