from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from .identified_base import IdentifiedBase


if TYPE_CHECKING:
    from .user import User
    from .role import Role


class Invite(IdentifiedBase):
    __tablename__ = 'invites'
    # id: int = Column(Integer, primary_key=True)
    token: Mapped[str] = Column(String(255), unique=True, nullable=False)
    role_id: Mapped[int] = Column(Integer, ForeignKey('roles.id'), nullable=False)
    role: Mapped["Role"] = relationship("Role", back_populates="invites")
    is_used: Mapped[bool] = Column(Boolean, default=False, nullable=False)
    expires_at: Mapped[datetime] = Column(DateTime, nullable=True)
    user: Mapped["User"] = relationship("User", back_populates="invite", uselist=False)