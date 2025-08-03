from sqlalchemy.ext.asyncio import AsyncSession

from src.data_collection_bot.backend.models import Record
from src.data_collection_bot.backend.repository import BaseRepository


class RecordRepository(BaseRepository[Record]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Record)