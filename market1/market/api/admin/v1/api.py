from fastapi import APIRouter

from . import (
    admin_user,
    foreign_apply,
    market,
    order,
    package,
    review,
    run_info,
    strategy,
    tag,
)

api_router = APIRouter()


api_router.include_router(admin_user.router)
api_router.include_router(market.router)
api_router.include_router(tag.router)
api_router.include_router(strategy.router)
api_router.include_router(package.router)
api_router.include_router(foreign_apply.router)
api_router.include_router(review.router)
api_router.include_router(order.router)
api_router.include_router(run_info.router)
