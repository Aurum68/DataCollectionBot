from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, relationship, mapped_column

from src.data_collection_bot.backend.models.identified_base import IdentifiedBase

if TYPE_CHECKING:
    from src.data_collection_bot.backend.models.parameter import Parameter
    from src.data_collection_bot.backend.models.daily_survey import DailySurvey


class Answer(IdentifiedBase):
    __tablename__ = 'answer'
    parameter_id: Mapped[int] = mapped_column(ForeignKey('parameter.id'))
    parameter: Mapped["Parameter"] = relationship(
        back_populates="answers"
    )
    daily_survey_id: Mapped[int] = mapped_column(ForeignKey('daily_survey.id'))
    daily_survey: Mapped["DailySurvey"] = relationship(
        back_populates="answers"
    )
    text: Mapped[str] = mapped_column(String(255))