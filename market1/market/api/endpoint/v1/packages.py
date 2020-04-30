import datetime
import logging

from fastapi import APIRouter, Depends

from market.api.share.package import search_pkg
from market.core.security import require_active_user
from market.models.const import OrderStatus, ProductType
from market.models.order import UserOrder
from market.models.package import StrategyPackage
from market.models.user import MarketUser
from market.schemas.package import (
    BuyedPkgInfo,
    BuyedPkgSearch,
    BuyedPkgSearchOut,
    PkgSearch,
    PkgSearchOut,
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/pkg/list", response_model=BuyedPkgSearchOut, tags=["用户端——套餐管理"])
async def list_pkg(
    schema_in: BuyedPkgSearch, current_user: MarketUser = Depends(require_active_user),
):
    """列出已购买套餐"""
    query = UserOrder.filter(user_id=current_user.id, product_type=ProductType.package,)
    if schema_in.show_payed:
        query = query.filter(status=OrderStatus.payed)
    if schema_in.show_expired:
        query = query.filter(expire_dt__gte=datetime.datetime.now())

    orders = await query.order_by("-create_dt")
    order_dict = {order.product_id: order for order in orders}
    # return packages
    packages = await StrategyPackage.filter(product_id__in=list(order_dict.keys()))
    data = []
    for pkg in packages:
        info = dict(**pkg.__dict__)
        info.update(**order_dict[pkg.product_id].__dict__)
        data.append(BuyedPkgInfo(**info))
    return BuyedPkgSearchOut(total=len(packages), data=data)


@router.post("/pkg/find", response_model=PkgSearchOut, tags=["用户端——套餐管理"])
async def user_search_pkg(schema_in: PkgSearch):
    """搜索套餐"""
    return await search_pkg(schema_in)
