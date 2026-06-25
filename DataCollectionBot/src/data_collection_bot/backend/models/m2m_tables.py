from sqlalchemy import Table, Column, Integer, ForeignKey

from src.data_collection_bot.database.db_config import Base

parameter_survey = Table(
    "parameter_survey",
    Base.metadata,
    Column("parameter_id", Integer, ForeignKey("parameter.id")),
    Column("survey_id", Integer, ForeignKey("survey.id")),
)

patient_survey = Table(
    "patient_survey",
    Base.metadata,
    Column("patient_id", Integer, ForeignKey("patient.id")),
    Column("survey_id", Integer, ForeignKey("survey.id")),
)

doctor_patient = Table(
    "doctor_patient",
    Base.metadata,
    Column("doctor_id", Integer, ForeignKey("doctor.id")),
    Column("patient_id", Integer, ForeignKey("patient.id")),
)