from sqlalchemy import Column, Integer, ForeignKey, Table

from src.data_collection_bot.database.db_config import Base


role_parameters = Table(
    "role_parameters",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id")),
    Column("parameter_id", Integer, ForeignKey("parameters.id")),
)