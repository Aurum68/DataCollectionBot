from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship, mapped_column
from src.data_collection_bot.backend.models.invites.invite import Invite

if TYPE_CHECKING:
    from src.data_collection_bot.backend.models.users.doctor import Doctor


class DoctorInvite(Invite):
    __tablename__ = 'doctor_invite'
    id: Mapped[int] = mapped_column(ForeignKey('invite.id'), primary_key=True)
    specialization: Mapped[str] = mapped_column(String(255), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey('doctor.id'), unique=True)
    doctor: Mapped["Doctor"] = relationship(
        back_populates="invite",
    )

    __mapper_args__ = {
        'polymorphic_identity': 'doctor',
    }