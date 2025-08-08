import asyncio

from aiogram import Bot, Dispatcher

from config import *
from src.data_collection_bot import UserRepository, AsyncSessionLocal, RoleRepository, UserService, RoleService, \
    ParameterRepository, InviteRepository, InviteService, BotMiddleware, ParameterService
from src.data_collection_bot.bot.middleware.db_session_middleware import DBSessionMiddleware
from src.data_collection_bot.database import DBManager
from src.data_collection_bot.database import Base, get_engine
from src.data_collection_bot.bot.start_handler import get_router as start_router
from src.data_collection_bot.bot.admin.admin_invite_handler import get_router as admin_invite_router
from src.data_collection_bot.bot.admin.base import get_router as admin_router
from src.data_collection_bot.bot.admin.admin_role_handler import get_router as admin_role_router
from src.data_collection_bot.bot.admin.admin_parameter_handler import get_router as admin_parameter_router
from src.data_collection_bot.bot.admin.admin_user_handler import get_router as admin_user_router

from initialize import initialize

import logging


logging.basicConfig(
    level=logging.INFO,
    filename='../../bot.log',
    filemode='w',
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


async def main():
    db_manager = DBManager(get_engine(), Base)

    await db_init(db_manager)
    await init()

    bot = Bot(TELEGRAM_TOKEN)
    dp = Dispatcher()

    dp.message.middleware(DBSessionMiddleware(AsyncSessionLocal))
    dp.message.middleware(BotMiddleware(bot=bot))
    dp.callback_query.middleware(DBSessionMiddleware(AsyncSessionLocal))
    dp.callback_query.middleware(BotMiddleware(bot=bot))

    dp.include_router(router=start_router())
    dp.include_router(router=admin_invite_router())
    dp.include_router(router=admin_router())
    dp.include_router(router=admin_role_router())
    dp.include_router(router=admin_parameter_router())
    dp.include_router(router=admin_user_router())

    try:
        logging.info("Starting bot...")
        await dp.start_polling(bot)
        logging.info("Bot started.")
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
    await db_manager.db_clear()
    await db_manager.db_init()


async def init() -> None:
    async with AsyncSessionLocal() as session:
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


if __name__ == '__main__':
    logging.info("Starting bot...")
    asyncio.run(main())