from typing import TYPE_CHECKING

from sqlalchemy import Column, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .identified_base import IdentifiedBase
from .m2m_tables import survey_question

if TYPE_CHECKING:
    from .survey import Survey
    from .answer import Answer
    from .daily_survey import DailySurvey


class Parameter(IdentifiedBase):
    __tablename__ = 'parameter'
    code: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    rule: Mapped[str] = mapped_column(String(255), nullable=False)

    surveys: Mapped[list["Survey"]] = relationship(
        secondary=survey_question,
        back_populates="parameters"
    )
    daily_surveys: Mapped[list["DailySurvey"]] = relationship(
        back_populates="current_parameter"
    )
    answers: Mapped[list["Answer"]] = relationship(
        back_populates="parameter"
    )
