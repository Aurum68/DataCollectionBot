from sqlalchemy import Column, Integer
from sqlalchemy.orm import Mapped, mapped_column

from src.data_collection_bot.database.db_config import Base


class IdentifiedBase(Base):
    __abstract__ = True
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)