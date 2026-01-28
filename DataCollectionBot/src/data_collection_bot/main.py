import asyncio
import sys

import pytz
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from src.data_collection_bot.config import *
from src.data_collection_bot import UserRepository, RoleRepository, UserService, RoleService, \
    ParameterRepository, InviteRepository, InviteService, BotMiddleware, ParameterService, daily_params_job
from src.data_collection_bot.bot.middleware.db_session_middleware import DBSessionMiddleware
from src.data_collection_bot.database import DBManager
from src.data_collection_bot.database import Base, create_engine_with_retry
from src.data_collection_bot.bot.start_handler import get_router as start_router
from src.data_collection_bot.bot.handlers.admin.admin_invite_handler import get_router as admin_invite_router
from src.data_collection_bot.bot.handlers.admin.base import get_router as admin_router
from src.data_collection_bot.bot.handlers.admin.admin_role_handler import get_router as admin_role_router
from src.data_collection_bot.bot.handlers.admin.admin_parameter_handler import get_router as admin_parameter_router
from src.data_collection_bot.bot.handlers.admin.admin_user_handler import get_router as admin_user_router
from src.data_collection_bot.bot.handlers.ui import get_router as user_registration_router
from src.data_collection_bot.bot.handlers.user import get_router as user_router

from src.data_collection_bot.initialize import initialize

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
    await init(async_session_local)

    redis = Redis(host='redis', port=6379, db=0, decode_responses=True)
    storage = RedisStorage(redis)
    bot = Bot(TELEGRAM_TOKEN)
    dp = Dispatcher(storage=storage)

    dp.message.middleware(DBSessionMiddleware(async_session_local))
    dp.message.middleware(BotMiddleware(bot=bot))
    dp.callback_query.middleware(DBSessionMiddleware(async_session_local))
    dp.callback_query.middleware(BotMiddleware(bot=bot))

    dp.include_router(router=start_router())
    dp.include_router(router=admin_invite_router())
    dp.include_router(router=admin_router())
    dp.include_router(router=admin_role_router())
    dp.include_router(router=admin_parameter_router())
    dp.include_router(router=admin_user_router())
    dp.include_router(router=user_registration_router())
    dp.include_router(router=user_router())

    try:
        # await setup_scheduler(bot=bot, storage=storage)
        logging.info("Starting bot...")
        scheduler_task = asyncio.create_task(setup_scheduler(bot=bot, storage=storage, async_session_local=async_session_local))
        polling_task = asyncio.create_task(dp.start_polling(bot))
        # Ждём оба таска
        await asyncio.gather(
            polling_task,
            scheduler_task)
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logging.info("Bot stopped by user...")
    except Exception as e:
        logging.error(e)
    finally:
        logging.info("Stopping bot...")
        await bot.session.close()
        await db_manager.db_dispose()
        logging.info("Bot stopped.")


async def db_init(db_manager: DBManager):
    # await db_manager.db_clear()
    await db_manager.db_init()


async def init(async_session_local: async_sessionmaker[AsyncSession]) -> None:
    async with async_session_local() as session:
        user_repository = UserRepository(session)
        role_repository = RoleRepository(session)
        parameter_repository = ParameterRepository(session)
        invite_repository = InviteRepository(session)

        user_service = UserService(user_repository)
        role_service = RoleService(role_repository, parameter_repository)
        parameter_service = ParameterService(parameter_repository)
        invite_service = InviteService(invite_repository)

        await initialize(
            user_service=user_service,
            role_service=role_service,
            invite_service=invite_service,
            parameter_service=parameter_service,
            admin_telegram_id=ADMIN_TELEGRAM_ID
        )


async def setup_scheduler(
        bot: Bot,
        storage: RedisStorage,
        async_session_local: async_sessionmaker[AsyncSession]
) -> None:
    scheduler = AsyncIOScheduler(timezone=pytz.timezone('Europe/Kaliningrad'))
    scheduler.add_job(
        func=daily_params_job,
        trigger='cron',
        hour=HOUR,
        minute=MINUTE,
        args=(bot, storage, async_session_local),
        id='daily_params_start_init',
        replace_existing=True
    )
    scheduler.start()
    logging.info('Scheduler started.')


if __name__ == '__main__':
    logging.info("Starting bot...")
    asyncio.run(main())

