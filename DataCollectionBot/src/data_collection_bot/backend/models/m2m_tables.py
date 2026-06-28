from sqlalchemy import Table, Column, Integer, ForeignKey, String, UniqueConstraint, PrimaryKeyConstraint

from src.data_collection_bot.database.db_config import Base

survey_question = Table(
    "survey_question",
    Base.metadata,
    Column("parameter_id", Integer, ForeignKey("parameter.id")),
    Column("survey_id", Integer, ForeignKey("survey.id")),
    Column('order', Integer),
    Column('norm_row', String(255)),
    Column('choice', String(255), nullable=True),
    Column('instruction', String(255), nullable=True),
    PrimaryKeyConstraint('parameter_id', 'survey_id'),
)

patient_survey = Table(
    "patient_survey",
    Base.metadata,
    Column("patient_id", Integer, ForeignKey("patient.id")),
    Column("survey_id", Integer, ForeignKey("survey.id")),
    UniqueConstraint('patient_id', 'survey_id'),
)

doctor_patient = Table(
    "doctor_patient",
    Base.metadata,
    Column("doctor_id", Integer, ForeignKey("doctor.id")),
    Column("patient_id", Integer, ForeignKey("patient.id")),
)

patient_category_link = Table(
    "patient_category_link",
    Base.metadata,
    Column("patient_id", Integer, ForeignKey("patient.id")),
    Column("category_id", Integer, ForeignKey("patient_category.id")),
)