from typing import Type

from src.data_collection_bot.backend.dto import CreateRecordDTO
from src.data_collection_bot.backend.models import Record
from src.data_collection_bot.backend.repository import RecordRepository
from src.data_collection_bot.backend.service.base_service_non_updating import BaseServiceNonUpdating


class RecordService(BaseServiceNonUpdating[
    Record,
    RecordRepository,
    CreateRecordDTO
                    ]):
    def __init__(self, repository: RecordRepository):
        super().__init__(Record, repository)