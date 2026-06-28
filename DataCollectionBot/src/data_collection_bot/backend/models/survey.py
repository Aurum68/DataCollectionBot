from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data_collection_bot.backend.models.identified_base import IdentifiedBase
from src.data_collection_bot.backend.models.m2m_tables import survey_question, patient_survey

if TYPE_CHECKING:
    from src.data_collection_bot.backend.models.daily_survey import DailySurvey
    from src.data_collection_bot.backend.models.invites.patient_invite import PatientInvite
    from src.data_collection_bot.backend.models.parameter import Parameter
    from src.data_collection_bot.backend.models.users.doctor import Doctor
    from src.data_collection_bot.backend.models.users.patient import Patient
    from src.data_collection_bot.backend.models.patient_category import PatientCategory


class Survey(IdentifiedBase):
    __tablename__ = 'survey'
    title: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    patient_category_id: Mapped[int] = mapped_column(ForeignKey('patient_category.id'), nullable=False, unique=True)
    patient_category: Mapped[list["PatientCategory"]] = relationship(
        back_populates="surveys",
    )
    parameters: Mapped[list["Parameter"]] = relationship(
        secondary=survey_question,
        back_populates="surveys",
    )
    created_by_doctor_id: Mapped[int] = mapped_column(ForeignKey('doctor.id'), nullable=False)
    doctor: Mapped["Doctor"] = relationship(
        back_populates="surveys",
    )
    patients: Mapped[list["Patient"]] = relationship(
        secondary=patient_survey,
        back_populates="surveys",
    )
    patient_invites: Mapped[list["PatientInvite"]] = relationship(
        back_populates="survey",
    )

    daily_surveys: Mapped[list["DailySurvey"]] = relationship(
        back_populates="survey",
    )