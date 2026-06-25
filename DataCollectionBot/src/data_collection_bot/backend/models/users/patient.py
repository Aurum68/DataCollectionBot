from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from src.data_collection_bot.backend.models.m2m_tables import patient_survey, doctor_patient, patient_category_link
from src.data_collection_bot.backend.models.patient_category import PatientCategory
from src.data_collection_bot.backend.models.users.user import User

if TYPE_CHECKING:
    from src.data_collection_bot.backend.models.daily_survey import DailySurvey
    from src.data_collection_bot.backend.models.invites.patient_invite import PatientInvite
    from src.data_collection_bot.backend.models.survey import Survey
    from src.data_collection_bot.backend.models.users.doctor import Doctor


class Patient(User):
    __tablename__ = 'patient'
    id: Mapped[int] = mapped_column(ForeignKey('user.id'), primary_key=True)
    birthday: Mapped[datetime] = mapped_column(nullable=True)
    pseudonym: Mapped[str] = mapped_column(String(255), nullable=True)
    invites: Mapped[list["PatientInvite"]] = relationship(back_populates='patient')
    doctors: Mapped[list["Doctor"]] = relationship(
        secondary=doctor_patient,
        back_populates="patients",
    )
    surveys: Mapped[list["Survey"]] = relationship(
        secondary=patient_survey,
        back_populates="patients",
    )
    daily_surveys: Mapped[list["DailySurvey"]] = relationship(
        back_populates="patient",
    )
    categories: Mapped[list["PatientCategory"]] = relationship(
        secondary=patient_category_link,
        back_populates="patients",
    )

    __mapper_args__ = {
        'polymorphic_identity': 'patient',
    }