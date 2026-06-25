from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.data_collection_bot.backend.models.identified_base import IdentifiedBase
from src.data_collection_bot.backend.models.m2m_tables import patient_category_link

if TYPE_CHECKING:
    from src.data_collection_bot.backend.models.users.patient import Patient
    from src.data_collection_bot.backend.models.survey import Survey


class PatientCategory(IdentifiedBase):
    __tablename__ = 'patient_category'
    code: Mapped[str] = mapped_column(String(255))
    title: Mapped[str] = mapped_column(String(255))
    patients: Mapped[list["Patient"]] = relationship(
        secondary=patient_category_link,
        back_populates="categories",
    )
    survey: Mapped["Survey"] = relationship(
        back_populates="patient_category",
        uselist=False,
    )