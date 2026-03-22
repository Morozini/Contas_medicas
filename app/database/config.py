from tortoise import Tortoise
from app.config.settings import URL_DB


async def init():
    await Tortoise.init(
        db_url=URL_DB,
        modules={"models": ["app.database.models"]},
    )
    await Tortoise.generate_schemas()

async def close():
    await Tortoise.close_connections()