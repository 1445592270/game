from fastapi import APIRouter

# from . import login, order, packages, pay, strategy, users
from . import order, packages, pay, push, runinfo, strategy, tag, user

api_router = APIRouter()


# api_router.include_router(login.router)
# api_router.include_router(users.router)
api_router.include_router(user.router)
api_router.include_router(tag.router)
api_router.include_router(strategy.router)
api_router.include_router(runinfo.router)
api_router.include_router(packages.router)
api_router.include_router(order.router)
api_router.include_router(pay.router)
api_router.include_router(push.router)
