from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message, InlineKeyboardButton

from src.data_collection_bot import RoleService, Role, CreateRoleDTO, UpdateRoleDTO, UserService

from src.data_collection_bot.bot.keyboards.admin import generate_admin_all_roles_keyboard, generate_admin_to_main_keyboard
from src.data_collection_bot.bot.utils.helpers import is_admin_cb, safe_message_delete


router = Router()


def get_router() -> Router:
    return router


@router.callback_query(F.data == "admin:all_roles")
async def admin_all_roles(
        cb: CallbackQuery,
        role_service: RoleService,
        user_service: UserService
):
    if not await is_admin_cb(cb=cb, role_service=role_service, user_service=user_service): return

    await cb.answer()
    await safe_message_delete(cb.message)

    roles: list[Role] = await role_service.get_all()
    keyboard: InlineKeyboardMarkup = generate_admin_all_roles_keyboard(roles)
    await cb.message.answer(text="Все доступные категории:", reply_markup=keyboard)


@router.callback_query(F.data == "admin:new_role")
async def admin_new_role(
        cb: CallbackQuery,
        state: FSMContext,
        role_service: RoleService,
        user_service: UserService
):
    if not await is_admin_cb(cb=cb, role_service=role_service, user_service=user_service): return

    await cb.answer()
    await safe_message_delete(cb.message)
    await cb.message.answer(text="Введите название категории", reply_markup=generate_admin_to_main_keyboard())
    await state.set_state("awaiting_role_name")
    await cb.answer()


@router.message(StateFilter("awaiting_role_name"))
async def awaiting_enter_role_name(
        msg: Message,
        state: FSMContext,
        role_service: RoleService
):
    await state.clear()
    role_name: str = msg.text
    role_dto = CreateRoleDTO(name=role_name)
    role: Role = await role_service.create(role_dto)
    text = f"Успешно создана категория <b>{role.name}</b>"
    await msg.answer(text=text, parse_mode="html", reply_markup=generate_admin_to_main_keyboard())


@router.callback_query(F.data.startswith("admin:role:id:"))
async def admin_role_info(
        cb: CallbackQuery,
        role_service: RoleService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    role_id: int = int(cb.data.split(":")[-1])
    role: Role = await role_service.get_by_id(role_id)
    text = (f"Категория: <b>{role.name}</b>\n"
            f"Привязано параметров: <b>{len(role.parameters)}</b>\n"
            f"Пользователей имеют эту категорию: <b>{len(role.users)}</b>")
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Изменить имя категории",
                callback_data=f"admin:edit:role:{role_id}"
            ),
            InlineKeyboardButton(
                text="🗑️Удалить категорию",
                callback_data=f"admin:role:delete:{role_id}"
            )],
            [InlineKeyboardButton(
                text="🔙Все категории",
                callback_data=f"admin:all_roles"
            )]
        ]
    )
    await cb.message.answer(text=text, parse_mode="html", reply_markup=keyboard)


@router.callback_query(F.data.startswith("admin:edit:role:"))
async def admin_role_edit(
        cb: CallbackQuery,
        state: FSMContext
):
    await cb.answer()
    await safe_message_delete(cb.message)

    role_id: int = int(cb.data.split(":")[-1])
    await state.update_data(role_id=role_id)
    await cb.message.answer(text="Введите новое название категории", reply_markup=generate_admin_to_main_keyboard())
    await state.set_state("awaiting_role_new_name")
    await cb.answer()


@router.message(StateFilter("awaiting_role_new_name"))
async def admin_enter_role_new_name(
        msg: Message,
        state: FSMContext,
        role_service: RoleService
):
    state_data = await state.get_data()
    old_role_id: int = state_data["role_id"]
    old_role: Role = await role_service.get_by_id(old_role_id)
    old_role_name: str = old_role.name

    await state.clear()
    new_role_name: str = msg.text
    role_dto = UpdateRoleDTO(name=new_role_name)
    role: Role = await role_service.update(item_id=old_role.id, item=role_dto)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🔙Все категории",
                callback_data=f"admin:all_roles"
            )]
        ]
    )

    await msg.answer(f"Имя категории <b>{old_role_name}</b> успешно изменено на <b>{role.name}</b>",
                     parse_mode="html",
                     reply_markup=keyboard)


@router.callback_query(F.data.startswith("admin:role:delete:"))
async def admin_role_delete(
        cb: CallbackQuery,
        role_service: RoleService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    role_id: int = int(cb.data.split(":")[-1])
    role: Role = await role_service.get_by_id(role_id)

    await role_service.delete(role)

    await cb.message.answer(text="Категория успешно удалена.",
                            reply_markup=InlineKeyboardMarkup(
                                inline_keyboard=[
                                    [InlineKeyboardButton(text="🔙Все категории", callback_data=f"admin:all_roles")]
                                ]
                            ))
