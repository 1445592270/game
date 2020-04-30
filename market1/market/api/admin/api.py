from fastapi import APIRouter

from .v1 import api as v1_api

api_router = APIRouter()


api_router.include_router(v1_api.api_router, prefix="/v1")
