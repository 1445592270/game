from uuid import UUID

from tortoise import Tortoise, run_async

from market.core import config
from market.models.admin_user import MarketAdminUser
from market.models.const import SUPER_SCOPE, UserScope2


async def init_db():
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    # await Tortoise.init(db_url="sqlite://s.db", modules={"models": ["market.models"]})
    await Tortoise.init(config=config.DB_CONFIGS)
    # Generate the schema
    await Tortoise.generate_schemas()

    user = await MarketAdminUser.get_or_none(email=config.FIRST_SUPERUSER)
    if not user:
        user_in = MarketAdminUser(
            name="aqfake",
            phone="12300000000",
            email=config.FIRST_SUPERUSER,
            uuid=UUID(hex="87d7eb5382e411ea865f53e889a17c68"),
            password=config.FIRST_SUPERUSER_PASSWORD,
            scope1=SUPER_SCOPE,
            scope2=UserScope2.su,
        )
        await user_in.save()
        print("!!! Created super super aqfake")


async def get_user(name):
    # await Tortoise.init(db_url="sqlite://s.db", modules={"models": ["market.models"]})
    await Tortoise.init(config=config.DB_CONFIGS)
    return await MarketAdminUser.get_or_none(name=name)


if __name__ == "__main__":
    run_async(init_db())
