import base64
import binascii
import json
import logging
from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.data_collection_bot import UserService, InviteService, CreateUserDTO, RoleService, Role, Invite, Roles, User, \
    UpdateInviteDTO
from src.data_collection_bot.bot.handlers.ui import admin_start, user_start

router = Router()


def get_router() -> Router:
    return router


ERROR_INVITE = "🚫Доступ запрещён.\n⚠️Некорректная ссылка приглашение!"
ERROR_EXPIRED = "🚫Доступ запрещён.\n⏰Истёк срок действия ссылки!"
ERROR_USED = "🚫Доступ запрещён.\nСсылка уже использована."
ERROR_REGISTERED = "Вы уже зарегистрированы!"


@router.message(Command(commands=['start']))
async def start(
        msg: Message,
        state: FSMContext,
        command: CommandObject,
        user_service: UserService,
        invite_service: InviteService,
        role_service: RoleService
):
    if not (await user_service.get_user_by_telegram_id(msg.from_user.id)) is None:
        await msg.answer(ERROR_REGISTERED)
        return

    args: str = command.args
    if args is None or not args.startswith('invite_'):
        await msg.answer(ERROR_INVITE)
        return

    payload: dict[str, str] = decode_args(args.replace('invite_', ''))

    if payload is None or 'token' not in payload:
        await msg.answer(ERROR_INVITE)
        return

    token: str = payload['token']

    invite: Invite = await invite_service.get_invite_by_token(token)
    if invite is None or invite.token != token:
        await msg.answer(ERROR_INVITE)
        return
    if invite.expires_at.timestamp() < datetime.now(timezone.utc).timestamp():
        await msg.answer(ERROR_EXPIRED)
        return
    if invite.is_used:
        await msg.answer(ERROR_USED)
        return

    invite_dto: UpdateInviteDTO = UpdateInviteDTO(is_used=True)
    updated_invite: Invite = await invite_service.update(item_id=invite.id, item=invite_dto)

    role: Role = await role_service.get_by_id(invite.role_id)

    user: User = await user_service.create(create_user(msg, role, updated_invite))

    logging.info(f"User with id: {user.telegram_id}; username: {user.username if user.username else 'None'} used "
                 f"invite with token: {invite.token}")

    await admin_start(msg=msg) if user.role.name == Roles.ADMIN.value else await user_start(msg=msg,
                                                                                            state=state)

def decode_args(args: str) -> dict[str, str] | None:
    try:
        payload: dict[str, str] = json.loads(base64.urlsafe_b64decode(args).decode())
    except json.decoder.JSONDecodeError:
        return None
    except binascii.Error:
        return None
    except ValueError:
        return None
    except UnicodeDecodeError:
        return None
    return payload


def create_user(msg: Message, role: Role, invite: Invite) -> CreateUserDTO:
    return CreateUserDTO(
        telegram_id=msg.from_user.id,
        username=msg.from_user.username,
        first_name=msg.from_user.first_name,
        last_name=msg.from_user.last_name,
        role_id=role.id,
        invite_id=invite.id
    )