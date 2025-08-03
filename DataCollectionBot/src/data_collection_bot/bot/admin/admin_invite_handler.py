from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from src.data_collection_bot import InviteService, UserService, Role, RoleService, Invite, User
from ..keyboards.admin import generate_admin_invite_keyboard, generate_admin_roles_invite_keyboard, generate_admin_to_main_keyboard

from src.data_collection_bot.bot.utils.helpers import is_admin_cb, safe_message_delete


router: Router = Router()


def get_router() -> Router:
    return router


@router.callback_query(F.data == 'admin:all_invites')
async def admin_all_invites(
        cb: CallbackQuery,
        invite_service: InviteService,
        user_service: UserService,
        role_service: RoleService,
        bot: Bot
):
    if not await is_admin_cb(cb, user_service, role_service): return

    await safe_message_delete(cb.message)
    await cb.answer()

    invites = await invite_service.get_all()
    keyboard = await generate_admin_invite_keyboard(invites, role_service)
    text: str = "Все пригласительные ссылки:"
    await bot.send_message(cb.from_user.id, text, reply_markup=keyboard)


@router.callback_query(F.data == 'admin:new_invite')
async def admin_new_invite(
        cb: CallbackQuery,
        user_service: UserService,
        role_service: RoleService
):
    if not await is_admin_cb(cb, user_service, role_service): return

    await safe_message_delete(cb.message)
    await cb.answer()

    roles: list[Role] = await role_service.get_all()
    keyboard = generate_admin_roles_invite_keyboard(roles)
    await cb.message.answer("Выберите категорию пациентов:", reply_markup=keyboard)
    await cb.answer()


@router.callback_query(F.data.startswith("admin:invite:role:"))
async def admin_invite_select_role(
        cb: CallbackQuery,
        state: FSMContext,
        role_service: RoleService
):
    await safe_message_delete(cb.message)
    await cb.answer()

    role_id: int = int(cb.data.split(":")[-1])
    await state.update_data(role_id=role_id)
    role: Role = await role_service.get_by_id(role_id)
    await cb.message.answer(f"Выбрана роль: {role.name}")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить (24 ч)", callback_data="admin:invite:skip_ttl")],
        ]
    )

    text: str = "Введите время действия ссылки в часах (от 1 до 720) или нажмите 'Пропустить'"
    await cb.message.answer(text=text, reply_markup=keyboard)
    await state.set_state("awaiting_ttl")
    await cb.answer()


@router.message(StateFilter("awaiting_ttl"))
async def admin_invite_enter_ttl(
        msg: Message,
        state: FSMContext,
        invite_service: InviteService,
        role_service: RoleService,
):
    state_data = await state.get_data()
    try:
        ttl = int(msg.text)
        if not (1 <= ttl <= 720):
            raise ValueError
    except (ValueError, TypeError):
        await msg.answer("Введите корректное количество часов - от 1 до 720")
        return
    await admin_send_invite_link(
        msg=msg,
        role_id=state_data['role_id'],
        ttl=ttl,
        invite_service=invite_service,
        role_service=role_service
    )
    await state.clear()


@router.callback_query(F.data == "admin:invite:skip_ttl", StateFilter("awaiting_ttl"))
async def admin_invite_skip_ttl(
        cb: CallbackQuery,
        state: FSMContext,
        invite_service: InviteService,
        role_service: RoleService,
):
    await cb.answer()
    await safe_message_delete(cb.message)

    state_data = await state.get_data()
    await admin_send_invite_link(
        msg=cb.message,
        role_id=state_data["role_id"],
        ttl=24,
        invite_service=invite_service,
        role_service=role_service,
    )
    await state.clear()
    await cb.answer()


async def admin_send_invite_link(
        msg: Message,
        role_id: int,
        ttl: int,
        invite_service: InviteService,
        role_service: RoleService
):
    role = await role_service.get_by_id(role_id)
    link = await invite_service.generate_invite_link(role, ttl)

    keyboard = generate_admin_to_main_keyboard()

    text = (f"✅Пригласительная ссылка для категории «<b>{role.name}</b>»:\n "
            f"<code>{link}</code>\n"
            f"💬Скопируйте ссылку и отправьте другому человеку для подключения к боту!\n"
            f"<i>Чтобы скопировать ссылку - кликните на неё</i>")

    await msg.answer(text=text, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(F.data.startswith("admin:invite:id"))
async def admin_invite_info(
        cb: CallbackQuery,
        invite_service: InviteService,
        role_service: RoleService
):
    invite_id: int = int(cb.data.split(":")[-1])
    await cb.answer()
    await safe_message_delete(cb.message)

    keyboard = generate_admin_to_main_keyboard()

    invite: Invite = await invite_service.get_by_id(invite_id)
    main_text: str = f"Ссылка: <code>{await InviteService.get_link(invite)}</code>\n"

    if not invite.is_used:
        await cb.message.answer(text=(f"Ссылка не использована.\n" + main_text), parse_mode='HTML', reply_markup=keyboard)
        return

    user: User = invite.user
    role: Role = await role_service.get_by_id(invite.role_id)

    firstname: str = user.first_name if user.first_name else ""
    lastname: str = user.last_name if user.last_name else ""

    text = (f"Ссылкой воспользовались!\n" + main_text
            + f"Имя: {firstname} {lastname}\n"
            f"Категория: {role.name}")

    await cb.message.answer(text=text, parse_mode='HTML', reply_markup=keyboard)