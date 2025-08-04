from typing import Sequence, Any, Callable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from src.data_collection_bot import Invite, Role, RoleService, Roles, Parameter, Rules


def generate_admin_start_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    text: str = 'Создать приглашение'
    button1 = InlineKeyboardButton(text=text, callback_data=f'admin:new_invite')
    text = 'Все ссылки'
    button2 = InlineKeyboardButton(text=text, callback_data=f'admin:all_invites')
    buttons.append([button1, button2])

    text = "Добавить категорию"
    button1 = InlineKeyboardButton(text=text, callback_data=f'admin:new_role')
    text = "Все категории"
    button2 = InlineKeyboardButton(text=text, callback_data=f'admin:all_roles')
    buttons.append([button1, button2])

    text = "Добавить параметр"
    button1 = InlineKeyboardButton(text=text, callback_data=f'admin:new_parameter')
    text = "Все параметры"
    button2 = InlineKeyboardButton(text=text, callback_data=f'admin:all_parameters')
    buttons.append([button1, button2])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# region Invite-keyboards
async def generate_admin_all_invite_keyboard(invites: list[Invite], role_service: RoleService) -> InlineKeyboardMarkup:
    buttons = []
    for invite in invites:
        role: Role = await role_service.get_by_id(invite.role_id)
        if role.name == Roles.ADMIN.value: continue

        text: str = f'ID {invite.id} | '
        if invite.is_used:
            text += f'Использовано | {role.name}'
        else:
            text += f'Не использовано | {role.name}'

        button = InlineKeyboardButton(text=text, callback_data=f'admin:invite:id:{invite.id}')
        buttons.append([button])

    buttons += generate_admin_to_main_keyboard().inline_keyboard

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def generate_admin_invite_choose_roles_keyboard(roles: list[Role]) -> InlineKeyboardMarkup:
    return generate_admin_roles_keyboard(roles=roles, callback_template="admin:invite:role:{id}")
# endregion


# region Roles-keyboards
def generate_admin_all_roles_keyboard(roles: list[Role]) -> InlineKeyboardMarkup:
    return generate_admin_roles_keyboard(roles=roles, callback_template="admin:role:id:{id}")


def generate_admin_roles_keyboard(
        roles: list[Role],
        callback_template: str
):
    buttons = []
    for role in roles:
        if role.name == Roles.ADMIN.value: continue
        text: str = f'{role.name}'
        button = InlineKeyboardButton(text=text, callback_data=callback_template.format(id=role.id))
        buttons.append([button])

    buttons += generate_admin_to_main_keyboard().inline_keyboard

    return InlineKeyboardMarkup(inline_keyboard=buttons)
# endregion


# region Parameter-keyboards
def generate_admin_all_parameters_keyboard(parameters: list[Parameter]) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for parameter in parameters:
        text: str = f'{parameter.name}'
        button = InlineKeyboardButton(text=text, callback_data=f'admin:parameter:concrete:{parameter.id}')
        row.append(button)
        if len(row) == 2:
            buttons.append(row.copy())
            row.clear()

    if len(row) > 0:
        buttons.append(row.copy())

    buttons += generate_admin_to_main_keyboard().inline_keyboard
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# region Create-parameter-keyboards
def generate_admin_create_parameter_choose_roles_keyboard(
        roles: list[Role],
        selected_roles: list[int]
) -> InlineKeyboardMarkup:
    buttons = generate_checkbox_keyboard(
        items=[role for role in roles if role.name != Roles.ADMIN.value],
        selected_items=selected_roles,
        callback_prefix="admin:parameter:create:choose_roles:",
        finish_callback="admin:parameter:create:finish_choose_roles",
        get_text=lambda role: role.name,
        get_value=lambda role: role.id,
    ).inline_keyboard
    buttons += generate_admin_to_main_keyboard().inline_keyboard
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def generate_admin_create_parameter_choose_rule_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    for rule in Rules:
        button = InlineKeyboardButton(text=rule.value, callback_data=f"admin:parameter:create:rule:{rule.name}")
        buttons.append([button])
    buttons += generate_admin_to_main_keyboard().inline_keyboard
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def generate_admin_create_parameter_norm_choose_keyboard(
        choices: str,
        selected: list[str]
) -> InlineKeyboardMarkup:
    buttons = generate_checkbox_keyboard(
        items=choices.split(';'),
        selected_items=selected,
        callback_prefix="admin:parameter:create:choice:",
        finish_callback="admin:parameter:create:finish_choose_norms",
        get_text=lambda x: x,
        get_value=lambda x: x,
        row_width=2
    ).inline_keyboard
    buttons += generate_admin_to_main_keyboard().inline_keyboard
    return InlineKeyboardMarkup(inline_keyboard=buttons)
# endregion


# region Edit-parameter-keyboards
def generate_admin_edit_parameter_keyboard(
        parameter_id: int,
        current_rule: str
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="Изменить название", callback_data=f'admin:parameter:edit:name:{parameter_id}'),
            InlineKeyboardButton(text="Изменить категории", callback_data=f'admin:parameter:edit:roles_open:{parameter_id}')
        ],
        [
            InlineKeyboardButton(text="Изменить правило", callback_data=f'admin:parameter:edit:rule_open:{parameter_id}'),
            InlineKeyboardButton(text="Изменить норму", callback_data=f'admin:parameter:edit:norm_open:{parameter_id}')
        ]
    ]
    if current_rule == Rules.CHOOSE.name:
        buttons.append([InlineKeyboardButton(text="Изменить варианты ответов",
                                             callback_data=f"admin:parameter:edit:choice_open:{parameter_id}")
                        ]
                       )

    buttons.append([InlineKeyboardButton(text="🗑️Удалить параметр", callback_data=f"admin:parameter:delete:{parameter_id}")])
    buttons.append([InlineKeyboardButton(text="🔙Ко всем параметрам", callback_data="admin:all_parameters")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def generate_admin_edit_parameter_roles_keyboard(
        parameter_id: int,
        roles: list[Role],
        selected_roles: list[int]
) -> InlineKeyboardMarkup:
    buttons = generate_checkbox_keyboard(
        items=[role for role in roles if role.name != Roles.ADMIN.value],
        selected_items=selected_roles,
        callback_prefix="admin:parameter:edit:roles_choose:",
        finish_callback="admin:parameter:edit:finish_choose_roles",
        get_text=lambda role: role.name,
        get_value=lambda role: role.id
    ).inline_keyboard
    buttons += generate_admin_edit_parameter_cancel_keyboard(parameter_id).inline_keyboard
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def generate_admin_edit_parameter_rule_keyboard(
        parameter_id: int,
        current_rule: str
) -> InlineKeyboardMarkup:
    buttons = []
    for rule in Rules:
        if rule.name == current_rule: continue
        buttons.append([InlineKeyboardButton(text=rule.value, callback_data=f'admin:parameter:edit:rule_choose:{rule.name}')])
    buttons += generate_admin_edit_parameter_cancel_keyboard(parameter_id).inline_keyboard
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def generate_admin_edit_parameter_norm_choose_keyboard(
        parameter_id: int,
        choices: str,
        selected: list[str]
) -> InlineKeyboardMarkup:
    buttons = generate_checkbox_keyboard(
        items=choices.split(';'),
        selected_items=selected,
        callback_prefix="admin:parameter:edit:norm:choice:",
        finish_callback="admin:parameter:edit:finish_choose_norms",
        get_text=lambda x: x,
        get_value=lambda x: x,
        row_width=2
    ).inline_keyboard
    buttons += generate_admin_edit_parameter_cancel_keyboard(parameter_id).inline_keyboard
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def generate_admin_edit_parameter_cancel_keyboard(parameter_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌Отмена", callback_data=f'admin:parameter:concrete:{parameter_id}')
        ]
    ])


def generate_admin_to_parameter_keyboard(
        parameter_id: int
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙К параметру", callback_data=f"admin:parameter:concrete:{parameter_id}")]
    ])
# endregion

# endregion


# region Helpers-keyboard
def generate_admin_to_main_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙На главную", callback_data="admin:main")]
        ]
    )


def generate_checkbox_keyboard(
        items: Sequence[Any],
        selected_items: Sequence[Any],
        callback_prefix: str,
        finish_callback: str,
        finish_text: str = "✅Готово!",
        get_text: Callable[[Any], str] = str,
        get_value: Callable[[Any], Any] = lambda x: x,
        row_width: int = 1,
) -> InlineKeyboardMarkup:
    buttons = []
    row = []
    for item in items:
        value = get_value(item)
        text = ("✅" if value in selected_items else "") + get_text(item)
        callback = f"{callback_prefix}:{value}"
        row.append(InlineKeyboardButton(text=text, callback_data=callback))
        if len(row) == row_width:
            buttons.append(row.copy())
            row.clear()
    if len(row) > 0:
        buttons.append(row.copy())

    buttons.append(
        [InlineKeyboardButton(text=finish_text, callback_data=finish_callback)]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)
# endregion


