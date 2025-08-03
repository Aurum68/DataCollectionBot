from typing import TYPE_CHECKING

from sqlalchemy import Column, BigInteger, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from .identified_base import IdentifiedBase


if TYPE_CHECKING:
    from .invite import Invite
    from .record import Record
    from .role import Role


class User(IdentifiedBase):
    __tablename__ = 'users'
    # id: int = Column(Integer, primary_key=True)
    telegram_id: Mapped[int] = Column(BigInteger, unique=True, nullable=False)
    username: Mapped[str] = Column(String(255), unique=True, nullable=True)
    first_name: Mapped[str] = Column(String(255), nullable=True)
    last_name: Mapped[str] = Column(String(255), nullable=True)
    role_id: Mapped[int] = Column(Integer, ForeignKey('roles.id'), nullable=False)
    role: Mapped["Role"] = relationship('Role', back_populates='users')
    invite_id: Mapped[int] = Column(Integer, ForeignKey('invites.id'), unique=True, nullable=True)
    invite: Mapped["Invite"] = relationship('Invite', back_populates='user', uselist=False)
    records: Mapped[list["Record"]] = relationship('Record', back_populates='user')
