from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, BigInteger, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.orm import mapped_column

from src.data_collection_bot.backend.models.identified_base import IdentifiedBase


class User(IdentifiedBase):
    __tablename__ = 'user'
    telegram_id: Mapped[int] = mapped_column(unique=True, nullable=True)
    username: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    patronymic: Mapped[str] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(255), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': role,
        'polymorphic_load': 'selectin'
    }