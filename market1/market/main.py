import logging

from aioredis import create_redis_pool
from fastapi import APIRouter, FastAPI, Header, HTTPException
from fastapi.responses import ORJSONResponse
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from market.api.admin.api import api_router as admin_router
from market.api.endpoint.api import api_router as endpoint_router
from market.core import config
from market.ctx import ctx

logger = logging.getLogger(__name__)
# app = FastAPI(title=config.PROJECT_NAME, openapi_url="/api/v1/openapi.json")
### XXX: The default JSONResponse encoder cannot handle nan for json
### so we use orjson, refer: https://github.com/tiangolo/fastapi/issues/459
app = FastAPI(
    title=config.PROJECT_NAME,
    default_response_class=ORJSONResponse,
    openapi_url="/xxx/api/v1/openapi.json",
    docs_url="/xxx/docs",
    redoc_url="/xxx/redoc",
)

# CORS
origins = []

# Set all CORS enabled origins
if config.BACKEND_CORS_ORIGINS:
    origins_raw = config.BACKEND_CORS_ORIGINS.split(",")
    for origin in origins_raw:
        use_origin = origin.strip()
        origins.append(use_origin)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


async def get_token_header(x_token: str = Header(...)):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


root_router = APIRouter()
root_router.include_router(admin_router, prefix="/fake")
root_router.include_router(endpoint_router)

app.include_router(root_router, prefix=config.API_PREFIX)
register_tortoise(
    app,
    config=config.DB_CONFIGS,
    # db_url="sqlite://s.db",
    # modules={"market": ["market.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.on_event("startup")
async def init_mongo() -> None:  # pylint: disable=W0612
    import motor.motor_asyncio

    ctx.mongo_client = motor.motor_asyncio.AsyncIOMotorClient(
        config.MONGO_SERVER,
        minPoolSize=config.MONGODB_MIN_POOL_SIZE,
        maxPoolSize=config.MONGODB_MAX_POOL_SIZE,
    )
    logger.info("motor-Mogodb startup")
    ctx.redis_client = await create_redis_pool(config.REDIS_URL)
    logger.info("aio-redis startup")


@app.on_event("shutdown")
async def close_mongo() -> None:  # pylint: disable=W0612
    if ctx.mongo_client:
        await ctx.mongo_client.close()
    logger.info("motor-Mogodb shutdown")
    if ctx.redis_client:
        await ctx.redis_client.close()
    logger.info("aio-redis shutdown")


# from fastapi import BackgroundTasks
#
#
# def write_notification(email: str, message=""):
#     with open("log.txt", mode="w") as email_file:
#         content = f"notification for {email}: {message}"
#         email_file.write(content)
#
#
# @app.post("/send-notification/{email}")
# async def send_notification(email: str, background_tasks: BackgroundTasks):
#     background_tasks.add_task(write_notification, email, message="some notification")
#     return {"message": "Notification sent in the background"}
