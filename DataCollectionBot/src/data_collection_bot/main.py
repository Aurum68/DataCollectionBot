import asyncio
import sys

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.data_collection_bot.database.db_config import create_engine_with_retry, Base
from src.data_collection_bot.database.db_manager import DBManager

import logging


async def main():

    logging.basicConfig(
        level=logging.INFO,
        # filename='../../bot.log',
        # filemode='w',
        stream=sys.stdout,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        force=True
    )

    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    logging.getLogger('apscheduler').setLevel(logging.WARNING)

    logging.info("Starting bot... Логи настроены!")

    db_engine = await create_engine_with_retry()
    async_session_local = async_sessionmaker(bind=db_engine, class_=AsyncSession, expire_on_commit=False)

    db_manager = DBManager(db_engine, Base)

    await db_init(db_manager)


async def db_init(db_manager: DBManager):
    # await db_manager.db_clear()
    await db_manager.db_init()

if __name__ == '__main__':
    logging.info("Starting bot...")
    asyncio.run(main())

