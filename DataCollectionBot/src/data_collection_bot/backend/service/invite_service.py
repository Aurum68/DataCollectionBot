import base64
import json
import secrets
from datetime import datetime, timedelta, UTC

from src.data_collection_bot.backend.dto import UpdateInviteDTO
from src.data_collection_bot.backend.service.base_service_updating import BaseServiceUpdating
from src.data_collection_bot.backend.models import Role
from src.data_collection_bot.backend.dto import CreateInviteDTO
from src.data_collection_bot.backend.models import Invite
from src.data_collection_bot.backend.repository import InviteRepository
from src.data_collection_bot.config import TELEGRAM_BOT_USERNAME


class InviteService(BaseServiceUpdating[
    Invite,
    InviteRepository,
    CreateInviteDTO,
    UpdateInviteDTO
                    ]):
    def __init__(self, repository: InviteRepository):
        super().__init__(Invite, repository)


    async def get_invite_by_token(self, token: str) -> Invite:
        return await self.repository.get_invite_by_token(token)


    async def generate_invite_link(self, role: Role, ttl: int = 24) -> str:
        token: str = secrets.token_urlsafe(16)
        expires_at = datetime.now(UTC) + timedelta(hours=ttl)

        link: str = InviteService.__make_invite_link(token)

        invite: CreateInviteDTO = CreateInviteDTO(token=token, role_id=role.id, expires_at=expires_at)
        await self.create(invite)

        return link

    @classmethod
    async def get_link(cls, invite: Invite) -> str:
        token: str = invite.token
        return InviteService.__make_invite_link(token)


    @classmethod
    def __make_invite_link(cls, token: str) -> str:
        payload = {'token': token}
        encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
        return f"https://t.me/{TELEGRAM_BOT_USERNAME}?start=invite_{encoded}"