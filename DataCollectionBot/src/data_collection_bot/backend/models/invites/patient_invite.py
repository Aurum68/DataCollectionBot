from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.data_collection_bot.backend.models.invites.invite import Invite

if TYPE_CHECKING:
    from src.data_collection_bot.backend.models.survey import Survey
    from src.data_collection_bot.backend.models.users.patient import Patient


class PatientInvite(Invite):
    __tablename__ = 'patient_invite'
    id: Mapped[int] = mapped_column(ForeignKey('invite.id'), primary_key=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey('patient.id'))
    patient: Mapped["Patient"] = relationship(
        back_populates="invites",
    )
    survey_id: Mapped[int] = mapped_column(ForeignKey('survey.id'))
    survey: Mapped["Survey"] = relationship(
        back_populates="patient_invites",
    )

    __mapper_args__ = {
        'polymorphic_identity': 'patient',
    }