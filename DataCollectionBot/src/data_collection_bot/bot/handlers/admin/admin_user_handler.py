from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.data_collection_bot import UserService, User, RoleService, Role, UpdateUserDTO
from src.data_collection_bot.bot.utils import safe_message_delete
from src.data_collection_bot.bot.keyboards import (generate_admin_all_users_keyboard,
                                                   generate_admin_user_edit_keyboard,
                                                   generate_admin_to_user_keyboard,
                                                   generate_admin_to_all_users_keyboard,
                                                   generate_admin_user_edit_role_keyboard)

router = Router()

def get_router() -> Router:
    return router


@router.callback_query(F.data == "admin:all_users")
async def admin_all_users(
        cb: CallbackQuery,
        user_service: UserService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    user_ids: list[int] = [user.id for user in (await user_service.get_all())]

    keyboard = await generate_admin_all_users_keyboard(user_ids, user_service)

    await cb.message.answer(text="Зарегистрированные пациенты:", reply_markup=keyboard)


@router.callback_query(F.data.startswith("admin:user:concrete:"))
async def admin_user(
        cb: CallbackQuery,
        user_service: UserService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    user_id: int = int(cb.data.split(":")[-1])
    user: User = await user_service.get_by_id(user_id)

    first_name: str = user.first_name if user.first_name else ""
    last_name: str = user.last_name if user.last_name else ""

    text: str = (f"Пациент <b>{first_name} {last_name}</b>\n"
                 f"Категория: <i>{user.role.name}</i>")

    await cb.message.answer(text=text, parse_mode="html", reply_markup=generate_admin_user_edit_keyboard(user_id))


@router.callback_query(F.data.startswith("admin:edit:user:role_open:"))
async def admin_edit_user_role_open(
        cb: CallbackQuery,
        state: FSMContext,
        user_service: UserService,
        role_service: RoleService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    user_id: int = int(cb.data.split(":")[-1])
    user: User = await user_service.get_by_id(user_id)

    roles: list[Role] = [role for role in await role_service.get_all() if role.name != user.role.name]

    keyboard = generate_admin_user_edit_role_keyboard(roles, user_id)

    await cb.message.answer(text=f"Выберите новую категорию для пациента <b>{user.first_name} {user.last_name}</b>",
                            parse_mode="html", reply_markup=keyboard
                            )
    await state.update_data(user_id=user_id)
    await state.set_state("choosing_role")


@router.callback_query(F.data.startswith("admin:user:edit:role:"))
async def admin_edit_user_role(
        cb: CallbackQuery,
        state: FSMContext,
        user_service: UserService,
):
    await cb.answer()
    await safe_message_delete(cb.message)

    data = await state.get_data()
    user_id = data["user_id"]

    role_id: int = int(cb.data.split(":")[-1])

    user_dto: UpdateUserDTO = UpdateUserDTO(role_id=role_id)
    user: User = await user_service.update(item_id=user_id, item=user_dto)

    await cb.message.answer(text=f"Категория пациента <b>{user.first_name} {user.last_name}</b> успешно изменена на <i>{user.role.name}</i>",
                            parse_mode="html", reply_markup=generate_admin_to_user_keyboard(user_id))
    await state.clear()


@router.callback_query(F.data.startswith("admin:edit:user:delete:"))
async def admin_user_delete(
        cb: CallbackQuery,
        user_service: UserService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    user_id: int = int(cb.data.split(":")[-1])
    user: User = await user_service.get_by_id(user_id)

    first_name = user.first_name if user.first_name else ""
    last_name = user.last_name if user.last_name else ""

    await user_service.delete(user)

    await cb.message.answer(text=f"Пациент <b>{first_name} {last_name}</b> успешно удалён.",
                            parse_mode="html", reply_markup=generate_admin_to_all_users_keyboard())