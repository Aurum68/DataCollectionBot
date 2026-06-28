from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from .api_v1.router import api_router
from ..database.db_config import create_engine_with_retry, Base
from ..database.db_manager import DBManager


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = await create_engine_with_retry()
    SessionMaker = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    app.state.db_engine = engine
    app.state.sessionmaker = SessionMaker

    db_manager = DBManager(engine=engine, base=Base)
    await db_manager.db_init()

    yield

    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)
