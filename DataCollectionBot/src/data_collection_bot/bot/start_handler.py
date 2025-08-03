import base64
import binascii
import json
from datetime import datetime, timezone

from aiogram import Router, Bot
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.data_collection_bot import UserService, InviteService, CreateUserDTO, RoleService, Role, Invite, Roles, User
from src.data_collection_bot.bot.ui import admin_start, user_start

router = Router()


def get_router() -> Router:
    return router


ERROR_INVITE = "🚫Доступ запрещён.\n⚠️Некорректная ссылка приглашение!"
ERROR_EXPIRED = "🚫Доступ запрещён.\n⏰Истёк срок действия ссылки!"
ERROR_USED = "🚫Доступ запрещён.\nСсылка уже использована."


@router.message(Command(commands=['start']))
async def start(
        msg: Message,
        command: CommandObject,
        user_service: UserService,
        invite_service: InviteService,
        role_service: RoleService,
        bot: Bot
):

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

    invite.is_used = True

    role: Role = await role_service.get_by_id(invite.role_id)

    user: User = await user_service.create(create_user(msg, role, invite))
    invite.role_id = role.id

    await admin_start(msg=msg, bot=bot) if user.role.name == Roles.ADMIN.value else await user_start(msg=msg, bot=bot)

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