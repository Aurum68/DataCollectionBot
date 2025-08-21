from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship, Mapped

from .identified_base import IdentifiedBase


if TYPE_CHECKING:
    from .user import User


class Record(IdentifiedBase):
    __tablename__ = 'records'
    user_id: Mapped[int] = Column(Integer, ForeignKey('users.id'))
    user: Mapped["User"] = relationship('User', back_populates='records')
    data: Mapped[dict] = Column(JSON)
    created_at: Mapped[datetime] = Column(DateTime, default=datetime.now)