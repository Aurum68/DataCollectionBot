from typing import TYPE_CHECKING

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship, Mapped

from .identified_base import IdentifiedBase
from .role_parameter import role_parameters

if TYPE_CHECKING:
    from .role import Role


class Parameter(IdentifiedBase):
    __tablename__ = 'parameters'
    # id: int = Column(Integer, primary_key=True)
    name: Mapped[str] = Column(String(255), unique=True, nullable=False)
    rule: Mapped[str] = Column(String(255), nullable=False)
    norm_row: Mapped[str] = Column(String(255), nullable=False)
    choice: Mapped[str] = Column(String(255), nullable=True)
    instruction: Mapped[str] = Column(String(255), nullable=True)
    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=role_parameters,
        back_populates="parameters",
    )