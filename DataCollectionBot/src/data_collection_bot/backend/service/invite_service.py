import base64
import json
import secrets
from datetime import datetime, timedelta, UTC

from src.data_collection_bot.backend.dto.create.create_invite_dto import CreateInviteDTO
from src.data_collection_bot.backend.dto.update.update_invite_dto import UpdateInviteDTO
from src.data_collection_bot.backend.models.invites.invite import Invite
from src.data_collection_bot.backend.repository.invite_repository import InviteRepository
from src.data_collection_bot.backend.service.base_service_updating import BaseServiceUpdating
from src.data_collection_bot.config import TELEGRAM_BOT_USERNAME




class InviteService(BaseServiceUpdating[
    Invite,
    InviteRepository,
    CreateInviteDTO,
    UpdateInviteDTO
                    ]):
    def __init__(self, repository: InviteRepository):
        super().__init__(Invite, repository)

    # @classmethod
    # def __make_invite_link(cls, token: str) -> str:
    #     payload = {'token': token}
    #     encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
    #     return f"https://t.me/{TELEGRAM_BOT_USERNAME}?start=invite_{encoded}"