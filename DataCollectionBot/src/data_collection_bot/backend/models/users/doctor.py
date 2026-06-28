from typing import TYPE_CHECKING

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from src.data_collection_bot.backend.models.m2m_tables import doctor_patient
from src.data_collection_bot.backend.models.users.user import User

if TYPE_CHECKING:
    from src.data_collection_bot.backend.models.invites.doctor_invite import DoctorInvite
    from src.data_collection_bot.backend.models.survey import Survey
    from src.data_collection_bot.backend.models.users.patient import Patient


class Doctor(User):
    __tablename__ = 'doctor'
    id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    specialization: Mapped[str] = mapped_column(String(255), nullable=False)
    patients: Mapped[list["Patient"]] = relationship(
        "Patient",
        secondary=doctor_patient,
        back_populates="doctors"
    )
    surveys: Mapped[list["Survey"]] = relationship(
        back_populates="doctor",
    )

    __mapper_args__ = {
        'polymorphic_identity': 'doctor',
    }