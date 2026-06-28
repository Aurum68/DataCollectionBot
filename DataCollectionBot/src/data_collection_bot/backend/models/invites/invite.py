from datetime import datetime

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.data_collection_bot.backend.models.identified_base import IdentifiedBase


class Invite(IdentifiedBase):
    __tablename__ = 'invite'
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    is_used: Mapped[bool] = mapped_column(default=False, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=True)
    role: Mapped[str] = mapped_column(String(255), nullable=False)
    used_by_user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=True)
    used_at: Mapped[datetime] = mapped_column(nullable=True)

    __mapper_args__ = {
        'polymorphic_identity': 'invite',
        'polymorphic_on': role,
        'polymorphic_load': 'selectin'
    }