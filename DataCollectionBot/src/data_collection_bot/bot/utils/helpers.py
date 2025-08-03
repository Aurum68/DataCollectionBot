from aiogram.exceptions import TelegramBadRequest
from aiogram.types import Message, CallbackQuery

from src.data_collection_bot import UserService, User, Roles, RoleService, Role

ERROR_ACCESS = "🚫Доступ запрещён!\nЭта функция доступна только для администратора!"


async def is_admin_msg(
        msg: Message,
        user_service: UserService,
        role_service: RoleService
) -> bool:
    user: User = await user_service.get_user_by_telegram_id(msg.from_user.id)
    role: Role = await role_service.get_by_id(user.role_id)
    if role.name != Roles.ADMIN.value:
        await msg.answer(ERROR_ACCESS)
        return False
    return True


async def is_admin_cb(
        cb: CallbackQuery,
        user_service: UserService,
        role_service: RoleService
):
    user: User = await user_service.get_user_by_telegram_id(cb.from_user.id)
    role: Role = await role_service.get_by_id(user.role_id)
    if role.name != Roles.ADMIN.value:
        await cb.answer(ERROR_ACCESS)
        return False
    return True


async def safe_message_delete(msg: Message):
    try:
        await msg.delete()
    except TelegramBadRequest as e:
        print(e)