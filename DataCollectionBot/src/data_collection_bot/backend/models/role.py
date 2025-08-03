from typing import TYPE_CHECKING

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship, Mapped

from .identified_base import IdentifiedBase
from .role_parameter import role_parameters

if TYPE_CHECKING:
    from .parameter import Parameter
    from .user import User
    from .invite import Invite



class Role(IdentifiedBase):
    __tablename__ = 'roles'
    # id: int = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String(255), nullable=False, unique=True)
    invites: Mapped[list["Invite"]] = relationship("Invite", back_populates="role")
    parameters: Mapped[list["Parameter"]] = relationship(
        "Parameter",
        secondary=role_parameters,
    )
    users: Mapped[list["User"]] = relationship("User", back_populates="role")