import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data_collection_bot.backend.models.identified_base import IdentifiedBase

if TYPE_CHECKING:
    from src.data_collection_bot.backend.models.survey import Survey
    from src.data_collection_bot.backend.models.users.patient import Patient
    from src.data_collection_bot.backend.models.parameter import Parameter
    from src.data_collection_bot.backend.models.answer import Answer


class DailySurvey(IdentifiedBase):
    __tablename__ = 'daily_survey'
    survey_id: Mapped[int] = mapped_column(ForeignKey("survey.id"))
    survey: Mapped["Survey"] = relationship(
        back_populates="daily_surveys",
    )

    patient_id: Mapped[int] = mapped_column(ForeignKey("patient.id"))
    patient: Mapped["Patient"] = relationship(
        back_populates="daily_surveys",
    )

    current_parameter_id: Mapped[int] = mapped_column(ForeignKey("parameter.id"))
    current_parameter: Mapped["Parameter"] = relationship(
        back_populates="daily_surveys",
    )

    answers: Mapped[list["Answer"]] = relationship(
        back_populates="daily_survey",
    )

    status: Mapped[str] = mapped_column(String(20))
    start_date: Mapped[datetime.datetime] = mapped_column(default=datetime.datetime.now)
    end_date: Mapped[datetime.datetime] = mapped_column(nullable=True)

    __table_args__ = (
        UniqueConstraint("survey_id", "patient_id", "start_date"),
    )