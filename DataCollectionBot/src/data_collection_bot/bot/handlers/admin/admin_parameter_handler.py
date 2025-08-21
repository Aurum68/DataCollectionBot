import re

from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton

from src.data_collection_bot import (ParameterService,
                                     UserService,
                                     RoleService, Role, Rules, Norm, NormFactory, CreateParameterDTO, Parameter,
                                     UpdateParameterDTO)
from src.data_collection_bot.bot.keyboards.admin import (generate_admin_all_parameters_keyboard,
                                                         generate_admin_create_parameter_choose_roles_keyboard,
                                                         generate_admin_create_parameter_choose_rule_keyboard,
                                                         generate_admin_create_parameter_norm_choose_keyboard,
                                                         generate_admin_edit_parameter_keyboard,
                                                         generate_admin_edit_parameter_cancel_keyboard,
                                                         generate_admin_edit_parameter_roles_keyboard,
                                                         generate_admin_edit_parameter_rule_keyboard,
                                                         generate_admin_edit_parameter_norm_choose_keyboard,
                                                         generate_admin_to_parameter_keyboard,
                                                         generate_admin_to_main_keyboard)
from src.data_collection_bot.bot.utils.helpers import is_admin_cb, safe_message_delete
from src.data_collection_bot.bot.states.parameter_registration_states import ParameterRegistrationStates
from src.data_collection_bot.bot.states.parameter_edit_states import ParameterEditStates

router = Router()


def get_router() -> Router:
    return router


@router.callback_query(F.data == "admin:all_parameters")
async def admin_all_parameters(
        cb: CallbackQuery,
        parameter_service: ParameterService,
        user_service: UserService,
        role_service: RoleService
):
    if not await is_admin_cb(cb=cb, user_service=user_service, role_service=role_service): return

    await cb.answer()
    await safe_message_delete(cb.message)

    parameters = await parameter_service.get_all()
    print(parameters)
    keyboard = generate_admin_all_parameters_keyboard(parameters)

    await cb.message.answer(text="Доступные параметры:", reply_markup=keyboard)


@router.callback_query(F.data == "admin:new_parameter")
async def admin_new_parameter(
        cb: CallbackQuery,
        state: FSMContext
):
    await cb.answer()
    await safe_message_delete(cb.message)

    await cb.message.answer(text="Введите название параметра", reply_markup=generate_admin_to_main_keyboard())
    await state.set_state(ParameterRegistrationStates.awaiting_parameter_name)


@router.message(StateFilter(ParameterRegistrationStates.awaiting_parameter_name))
async def admin_create_enter_parameter_name(
        message: Message,
        state: FSMContext,
        parameter_service: ParameterService,
        role_service: RoleService,
):
    name: str = message.text
    if not (await parameter_service.get_parameter_by_name(name=name)) is None:
        await message.answer(text="Параметр с таким именем уже существует! Попробуйте ещё раз.")
        await state.set_state(ParameterRegistrationStates.awaiting_parameter_name)
        return

    await state.update_data(parameter_name=name,
                            selected_roles=[],
                            rule="",
                            choose=None,
                            norm_choose=[],
                            norm_row=""
                        )
    roles: list[Role] = await role_service.get_all()

    keyboard = generate_admin_create_parameter_choose_roles_keyboard(roles, list())
    await message.answer(text="Выберите категории пациентов для этого параметра.\n"
                              "<i>Можно несколько</i>", parse_mode="HTML", reply_markup=keyboard)
    await state.set_state(ParameterRegistrationStates.choosing_roles)


@router.callback_query(F.data.startswith('admin:parameter:create:choose_roles:'),
                       StateFilter(ParameterRegistrationStates.choosing_roles))
async def admin_create_parameter_choose_roles(
        cb: CallbackQuery,
        state: FSMContext,
        role_service: RoleService
):
    data = await state.get_data()
    selected_roles = data.get('selected_roles', [])
    role_id: int = int(cb.data.split(':')[-1])

    if role_id not in selected_roles:
        selected_roles.append(role_id)
    else:
        selected_roles.remove(role_id)

    await state.update_data(selected_roles=selected_roles)

    roles: list[Role] = await role_service.get_all()
    keyboard = generate_admin_create_parameter_choose_roles_keyboard(roles, selected_roles)
    await cb.message.edit_reply_markup(reply_markup=keyboard)
    await state.set_state(ParameterRegistrationStates.choosing_roles)


@router.callback_query(F.data == 'admin:parameter:create:finish_choose_roles',
                       StateFilter(ParameterRegistrationStates.choosing_roles))
async def admin_create_parameter_finish_choose_roles(
        cb: CallbackQuery,
        state: FSMContext,
        role_service: RoleService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    data = await state.get_data()
    selected_roles = data.get('selected_roles', [])

    roles: list[str] = [(await role_service.get_by_id(role_id)).name for role_id in selected_roles]

    await cb.message.answer(text=f"Выбранные категории:\n"
                                 f"<b>{', \n'.join(roles)}</b>",
                            parse_mode="HTML")

    await cb.message.answer(text="Выберите правило заполнения параметра:",
                            reply_markup=generate_admin_create_parameter_choose_rule_keyboard())

    await state.set_state(ParameterRegistrationStates.choosing_rule)


@router.callback_query(F.data.startswith('admin:parameter:create:rule:'))
async def admin_create_parameter_choose_rule(
        cb: CallbackQuery,
        state: FSMContext
):
    await cb.answer()
    await safe_message_delete(cb.message)

    rule = cb.data.split(':')[-1]
    await state.update_data(rule=rule)

    if rule == Rules.CHOOSE.name:
        await cb.message.answer(text="Введите через ';' варианты ответов" )
        await state.set_state(ParameterRegistrationStates.awaiting_choose_row)
        return

    await cb.message.answer(text="Введите норму для этого параметра.")
    await state.set_state(ParameterRegistrationStates.awaiting_norm_row)
    await cb.answer()


@router.message(StateFilter(ParameterRegistrationStates.awaiting_choose_row))
async def admin_create_parameter_enter_choose_row(
        message: Message,
        state: FSMContext,
):
    choices = message.text
    pattern = re.compile(r'^[^;]+(;[^;]+)+$')
    if pattern.match(choices) is None:
        await message.answer(text="Неверно введены варианты ответов! Используйте ';' для разделения вариантов.\n"
                                  "<i>Пример: яблоко;груша;слива</i>", parse_mode="HTML")
        await state.set_state(ParameterRegistrationStates.awaiting_choose_row)
        return

    await state.update_data(choose=choices)
    keyboard = generate_admin_create_parameter_norm_choose_keyboard(choices, list())
    await message.answer(text="Выберите нормы для этого параметра.", reply_markup=keyboard)
    await state.set_state(ParameterRegistrationStates.choosing_norm)


@router.callback_query(F.data.startswith('admin:parameter:create:choice:'),
                       StateFilter(ParameterRegistrationStates.choosing_norm))
async def admin_create_parameter_choose_norm(
        cb: CallbackQuery,
        state: FSMContext,
):
    data = await state.get_data()
    choose: str = data['choose']
    norm_choose = data['norm_choose']

    choices = cb.data.split(':')[-1]

    if choices in norm_choose:
        norm_choose.remove(choices)
    else:
        norm_choose.append(choices)

    await state.update_data(norm_choose=norm_choose, norm_row=';'.join(norm_choose))
    await cb.message.edit_reply_markup(reply_markup=generate_admin_create_parameter_norm_choose_keyboard(choose, norm_choose))
    await state.set_state(ParameterRegistrationStates.choosing_norm)


@router.callback_query(F.data == 'admin:parameter:create:finish_choose_norms',
                       StateFilter(ParameterRegistrationStates.choosing_norm))
async def admin_create_parameter_finish_choose_norms(
        cb: CallbackQuery,
        state: FSMContext,
):
    await cb.answer()
    await safe_message_delete(cb.message)

    await cb.message.answer(
        text="Если необходимо - введите инструкцию, как заполнять этот параметр.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Пропустить и создать параметр",
                        callback_data=f'admin:parameter:create:skip_instruction'
                    )
                ]
            ]
        )
    )
    await state.set_state(ParameterRegistrationStates.awaiting_instruction)
    await cb.answer()


@router.message(StateFilter(ParameterRegistrationStates.awaiting_norm_row))
async def admin_create_parameter_norm_row(
        message: Message,
        state: FSMContext
):
    norm_row = message.text

    res = await validate_norm_row(
        msg=message,
        state=state,
        error_state=ParameterRegistrationStates.awaiting_norm_row,
        norm_row=norm_row
    )

    if not res: return

    await state.update_data(norm_row=norm_row)

    await message.answer(
        text="Если необходимо - введите инструкцию, как заполнять этот параметр.",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Пропустить и создать параметр",
                        callback_data=f'admin:parameter:create:skip_instruction'
                    )
                ]
            ]
        )
    )
    await state.set_state(ParameterRegistrationStates.awaiting_instruction)


@router.message(StateFilter(ParameterRegistrationStates.awaiting_instruction))
async def admin_create_parameter_instruction(
        message: Message,
        state: FSMContext,
        parameter_service: ParameterService,
        role_service: RoleService
):
    instruction = message.text

    await state.update_data(instruction=instruction)

    await admin_finish_create_parameter(
        message=message,
        state=state,
        parameter_service=parameter_service,
        role_service=role_service
    )


@router.callback_query(F.data == 'admin:parameter:create:skip_instruction',
                       StateFilter(ParameterRegistrationStates.awaiting_instruction))
async def admin_create_parameter_skip_instruction(
        cb: CallbackQuery,
        state: FSMContext,
        parameter_service: ParameterService,
        role_service: RoleService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    await state.update_data(instruction="")

    await admin_finish_create_parameter(
        message=cb.message,
        state=state,
        parameter_service=parameter_service,
        role_service=role_service
    )


async def admin_finish_create_parameter(
        message: Message,
        state: FSMContext,
        parameter_service: ParameterService,
        role_service: RoleService,
):
    parameter = await admin_create_parameter(state, parameter_service, role_service)

    await message.answer(text=f"Успешно создан параметр <b>{parameter.name}</b>.\n", parse_mode="HTML",
                         reply_markup=generate_admin_to_main_keyboard())
    await state.clear()


async def admin_create_parameter(
        state: FSMContext,
        parameter_service: ParameterService,
        role_service: RoleService
) -> Parameter:
    data = await state.get_data()
    name: str = data['parameter_name']
    selected_roles: list[int] = data['selected_roles']
    rule: str = data['rule']
    choose: str = data['choose']
    norm_row: str = data['norm_row']
    instruction: str = data['instruction']

    parameter_dto: CreateParameterDTO = CreateParameterDTO(
        name=name,
        rule=rule,
        choice=choose,
        norm_row=norm_row,
        instruction=instruction
    )
    parameter: Parameter = await parameter_service.create(parameter_dto)

    for role_id in selected_roles:
        await role_service.add_parameter_to_role(role_id=role_id, parameter_id=parameter.id)
    return parameter


@router.callback_query(F.data.startswith("admin:parameter:concrete:"))
async def admin_parameter_concrete(
        cb: CallbackQuery,
        state: FSMContext,
        parameter_service: ParameterService,
):
    await cb.answer()
    await safe_message_delete(cb.message)

    await state.clear()

    parameter_id: int = int(cb.data.split(':')[-1])
    parameter: Parameter = await parameter_service.get_by_id(parameter_id)

    rls = parameter.roles
    roles: str = ', '.join([role.name for role in rls])

    text: str = (f"Параметр <b>{parameter.name}</b>:\n"
                 f"Категории: <b>{roles}</b>\n"
                 f"Правило: <b>{Rules[parameter.rule].value}</b>\n"
                 f"Норма: <b>{parameter.norm_row}</b>\n"
                 f"Инструкция: <b>{parameter.instruction}</b>")
    await cb.message.answer(text=text, parse_mode="HTML", reply_markup=generate_admin_edit_parameter_keyboard(parameter_id=parameter_id,
                                                                                                              current_rule=parameter.rule))


@router.callback_query(F.data.startswith("admin:parameter:edit:name:"))
async def admin_edit_parameter_name(
        cb: CallbackQuery,
        state: FSMContext,
        parameter_service: ParameterService,
):
    await cb.answer()
    await safe_message_delete(cb.message)

    parameter_id: int = int(cb.data.split(':')[-1])
    parameter: Parameter = await parameter_service.get_by_id(parameter_id)

    await state.update_data(
        parameter_id=parameter_id,
        parameter_name=parameter.name
    )
    await cb.message.answer(text=f"Введите новое имя для параметра <b>{parameter.name}</b>", parse_mode="HTML")
    await state.set_state(ParameterEditStates.awaiting_new_name)
    await cb.answer()


@router.message(StateFilter(ParameterEditStates.awaiting_new_name))
async def admin_edit_parameter_name(
        message: Message,
        state: FSMContext,
        parameter_service: ParameterService
):
    data = await state.get_data()
    parameter_id: int = data['parameter_id']
    parameter_name: str = data['parameter_name']

    new_name = message.text
    if new_name == parameter_name:
        await message.answer(text="Введённое имя совпадает с существующим!\n"
                                  "<i>Попробуйте ещё раз или нажмите 'Отмена'</i>",
                             parse_mode="HTML",
                             reply_markup=generate_admin_edit_parameter_cancel_keyboard(parameter_id))
        await state.set_state(ParameterEditStates.awaiting_new_name)
        return

    parameter_dto: UpdateParameterDTO = UpdateParameterDTO(
        name=new_name
    )
    updated_parameter: Parameter = await parameter_service.update(parameter_id, parameter_dto)

    keyboard = generate_admin_to_parameter_keyboard(parameter_id)
    await message.answer(text=f"Имя параметра успешно изменено на <b>{updated_parameter.name}</b>.",
                         parse_mode="HTML",
                         reply_markup=keyboard,)
    await state.clear()


@router.callback_query(F.data.startswith("admin:parameter:edit:roles_open:"))
async def admin_edit_parameter_roles_opening(
        cb: CallbackQuery,
        state: FSMContext,
        parameter_service: ParameterService,
        role_service: RoleService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    parameter_id: int = int(cb.data.split(':')[-1])

    parameter: Parameter = await parameter_service.get_by_id(parameter_id)

    selected_roles: list[int] = [role.id for role in parameter.roles]

    await state.update_data(
        parameter_id=parameter_id,
        parameter_name=parameter.name,
        selected_roles=selected_roles
    )

    await cb.message.answer(text=f"Выберите категории для параметра <b>{parameter.name}</b>.",
                            parse_mode="HTML",
                            reply_markup=generate_admin_edit_parameter_roles_keyboard(
                                parameter_id=parameter_id,
                                roles=await role_service.get_all(),
                                selected_roles=selected_roles
                            ))
    await state.set_state(ParameterEditStates.choosing_new_roles)
    await cb.answer()


@router.callback_query(F.data.startswith("admin:parameter:edit:roles_choose:"),
                       StateFilter(ParameterEditStates.choosing_new_roles))
async def admin_edit_parameter_roles(
        cb: CallbackQuery,
        state: FSMContext,
        role_service: RoleService
):
    role_id: int = int(cb.data.split(':')[-1])

    data = await state.get_data()
    parameter_id: int = data['parameter_id']
    selected_roles: list[int] = data['selected_roles']

    if role_id in selected_roles:
        selected_roles.remove(role_id)
    else:
        selected_roles.append(role_id)

    await state.update_data(selected_roles=selected_roles)

    await cb.message.edit_reply_markup(reply_markup=generate_admin_edit_parameter_roles_keyboard(
        parameter_id=parameter_id,
        roles=await role_service.get_all(),
        selected_roles=selected_roles
    ))
    await state.set_state(ParameterEditStates.choosing_new_roles)
    await cb.answer()


@router.callback_query(F.data == "admin:parameter:edit:finish_choose_roles",
                       StateFilter(ParameterEditStates.choosing_new_roles))
async def admin_edit_parameter_finish_choose_roles(
        cb: CallbackQuery,
        state: FSMContext,
        parameter_service: ParameterService,
        role_service: RoleService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    data = await state.get_data()
    parameter_id: int = data['parameter_id']
    parameter_name: str = data['parameter_name']
    selected_roles: list[int] = data['selected_roles']

    parameter: Parameter = await parameter_service.get_by_id(parameter_id)

    keyboard = generate_admin_to_parameter_keyboard(parameter_id)

    old_roles: list[int] = [role.id for role in parameter.roles]
    if set(old_roles) == set(selected_roles):
        await cb.message.answer(text="Выбраны те же категории. Если вы хотите изменить категории, вернитесь к параметру и"
                                     " нажмите <i>Изменить категории</i>",
                                parse_mode="HTML",
                                reply_markup=keyboard)
        await state.clear()
        return

    for role_id in selected_roles:
        if role_id not in old_roles:
            await role_service.add_parameter_to_role(role_id=role_id, parameter_id=parameter_id)

    for role_id in old_roles:
        if role_id not in selected_roles:
            await role_service.remove_parameter_from_role(role_id=role_id, parameter_id=parameter_id)

    await state.clear()
    roles: str = ', '.join([(await role_service.get_by_id(role_id)).name for role_id in selected_roles])
    await cb.message.answer(
        text=f"Категории параметра <b>{parameter_name}</b> успешно изменены на\n"
             f"<b>{roles}</b>",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("admin:parameter:edit:rule_open:"))
async def admin_edit_parameter_rule_open(
        cb: CallbackQuery,
        state: FSMContext,
        parameter_service: ParameterService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    parameter_id = int(cb.data.split(':')[-1])
    parameter: Parameter = await parameter_service.get_by_id(parameter_id)

    await state.update_data(parameter_id=parameter_id, parameter_name=parameter.name)

    await cb.message.answer(text=f"Выберите новое правило заполнения параметра <b>{parameter.name}</b>\n"
                                 f"<i>Текущее правило: {Rules[parameter.rule].value}</i>",
                            parse_mode="HTML",
                            reply_markup=generate_admin_edit_parameter_rule_keyboard(
                                parameter_id=parameter_id,
                                current_rule=parameter.rule
                            ))
    await state.set_state(ParameterEditStates.choosing_new_rule)
    await cb.answer()


@router.callback_query(F.data.startswith("admin:parameter:edit:rule_choose:"),
                       StateFilter(ParameterEditStates.choosing_new_rule))
async def admin_edit_parameter_rule_choose(
        cb: CallbackQuery,
        state: FSMContext,
):
    await cb.answer()
    await safe_message_delete(cb.message)

    data = await state.get_data()
    parameter_id: int = data['parameter_id']
    parameter_name: str = data['parameter_name']

    new_rule: str = cb.data.split(':')[-1]

    await state.update_data(rule=new_rule)

    await cb.message.answer(text=f"Правило для параметра <b>{parameter_name}</b> успешно изменено на <b>{Rules[new_rule].value}</b>",
                                parse_mode="HTML"
                           )

    if new_rule == Rules.CHOOSE.name:
        await cb.message.answer(text="Введите варианты ответов. Используйте ';' для разделения."
                                , reply_markup=generate_admin_edit_parameter_cancel_keyboard(parameter_id=parameter_id))
        await state.set_state(ParameterEditStates.awaiting_new_choice_rule)
        return

    await cb.message.answer(text=f"Также необходимо обновить норму для параметра <b>{parameter_name}</b>.\n"
                                 f"Введите норму в соответствии с выбранным правилом <i>{Rules[new_rule].value}</i>.\n",
                            parse_mode="HTML",
                            reply_markup=generate_admin_edit_parameter_cancel_keyboard(parameter_id=parameter_id))
    await state.set_state(ParameterEditStates.awaiting_new_norm_row_rule)
    await cb.answer()


@router.message(StateFilter(ParameterEditStates.awaiting_new_choice_rule))
async def admin_edit_parameter_enter_new_choice_rule(
        msg: Message,
        state: FSMContext,
):
    new_choice: str = msg.text

    pattern = re.compile(r'^[^;]+(;[^;]+)+$')
    if pattern.match(new_choice) is None:
        await msg.answer(text="Неверно введены варианты ответов! Используйте ';' для разделения вариантов.\n"
                                  "<i>Пример: яблоко;груша;слива</i>", parse_mode="HTML")
        await state.set_state(ParameterEditStates.awaiting_new_choice_rule)
        return

    data = await state.get_data()
    parameter_id: int = data['parameter_id']
    parameter_name: str = data['parameter_name']

    await state.update_data(choice=new_choice, selected=[])

    await msg.answer(text=f"К параметру <b>{parameter_name}</b> успешно добавлены варианты ответов <b>{new_choice}</b>.",
                     parse_mode="HTML")

    await msg.answer(text=f"Также необходимо обновить норму для параметра <b>{parameter_name}</b>.\n"
                          "Выберите норму.", parse_mode="HTML",
                     reply_markup=generate_admin_edit_parameter_norm_choose_keyboard(parameter_id=parameter_id,
                                                                                     choices=new_choice,
                                                                                     selected=[]
                                                                                     )
                     )
    await state.set_state(ParameterEditStates.choosing_new_choice_norm_rule)


@router.callback_query(F.data.startswith("admin:parameter:edit:norm:choice:"),
                       StateFilter(ParameterEditStates.choosing_new_choice_norm_rule))
async def admin_edit_parameter_choose_new_choice_norm_rule(
        cb: CallbackQuery,
        state: FSMContext
):
    await choosing_new_norm(
        cb=cb,
        state=state,
        next_state=ParameterEditStates.choosing_new_choice_norm_rule
    )


@router.callback_query(F.data == "admin:parameter:edit:finish_choose_norms",
                       StateFilter(ParameterEditStates.choosing_new_choice_norm_rule))
async def admin_edit_parameter_finish_choose_new_choice_norm_rule(
        cb: CallbackQuery,
        state: FSMContext,
        parameter_service: ParameterService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    data = await state.get_data()
    parameter_id: int = data['parameter_id']
    parameter_name: str = data['parameter_name']
    rule: str = data['rule']
    choice: str = data['choice']
    selected: list[str] = data['selected']

    parameter_dto = UpdateParameterDTO(
        rule=rule,
        choice=choice,
        norm_row=';'.join(selected)
    )

    parameter: Parameter = await parameter_service.update(item_id=parameter_id, item=parameter_dto)
    keyboard = generate_admin_to_parameter_keyboard(parameter_id)

    await cb.message.answer(text=f"Вы успешно изменили параметр <b>{parameter_name}</b>.\n"
                                 f"Правило: <i>{Rules[rule].value}</i>\n"
                                 f"Варианты ответов: <i>{choice}</i>\n"
                                 f"Норма: <i>{parameter.norm_row}</i>",
                            parse_mode="HTML",
                            reply_markup=keyboard)


@router.message(StateFilter(ParameterEditStates.awaiting_new_norm_row_rule))
async def admin_edit_parameter_enter_new_norm_row_rule(
        msg: Message,
        state: FSMContext,
        parameter_service: ParameterService
):
    data = await state.get_data()
    parameter_id: int = data['parameter_id']
    parameter_name: str = data['parameter_name']

    new_norm_row: str = msg.text

    result = await validate_norm_row(
        msg=msg,
        state=state,
        error_state=ParameterEditStates.awaiting_new_norm_row_rule,
        norm_row=new_norm_row
    )

    if not result: return

    rule, norm = result

    parameter_dto = UpdateParameterDTO(rule=rule, norm_row=new_norm_row)
    parameter: Parameter = await parameter_service.update(item_id=parameter_id, item=parameter_dto)
    keyboard = generate_admin_to_parameter_keyboard(parameter_id)

    await msg.answer(text=f"Вы успешно изменили параметр <b>{parameter_name}</b>.\n"
                                 f"Правило: <i>{Rules[rule].value}</i>\n"
                                 f"Норма: <i>{parameter.norm_row}</i>",
                     parse_mode="HTML",
                     reply_markup=keyboard
                     )


@router.callback_query(F.data.startswith("admin:parameter:edit:norm_open:"))
async def admin_edit_parameter_norm_open(
        cb: CallbackQuery,
        state: FSMContext,
        parameter_service: ParameterService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    parameter_id: int = int(cb.data.split(":")[-1])
    parameter: Parameter = await parameter_service.get_by_id(parameter_id)

    await state.update_data(parameter_id=parameter_id)

    if parameter.rule == Rules.CHOOSE.name:
        choice: str = parameter.choice
        selected: list[str] = parameter.norm_row.split(';')
        keyboard = generate_admin_edit_parameter_norm_choose_keyboard(
            parameter_id=parameter_id,
            choices=choice,
            selected=selected
        )
        await state.update_data(choice=choice, selected=selected)
        await state.set_state(ParameterEditStates.choosing_new_norm)
        await cb.message.answer(text=f"Выберите новую норму для параметра <b>{parameter.name}</b>.",
                                parse_mode="HTML",
                                reply_markup=keyboard)
        return

    await state.update_data(rule=parameter.rule)
    await cb.message.answer(text=f"Введите новую норму для параметра <b>{parameter.name}</b>.\n"
                                 f"Текущая норма: <i>{parameter.norm_row}</i>",
                            parse_mode="HTML",
                            reply_markup=generate_admin_edit_parameter_cancel_keyboard(parameter_id=parameter_id))
    await state.set_state(ParameterEditStates.awaiting_new_norm_row)


@router.callback_query(F.data.startswith("admin:parameter:edit:norm:choice:"),
                       StateFilter(ParameterEditStates.choosing_new_norm))
async def admin_edit_parameter_choosing_new_norm(
        cb: CallbackQuery,
        state: FSMContext
):
    await choosing_new_norm(
        cb=cb,
        state=state,
        next_state=ParameterEditStates.choosing_new_norm
    )


@router.callback_query(F.data == "admin:parameter:edit:finish_choose_norms",
                       StateFilter(ParameterEditStates.choosing_new_norm))
async def admin_edit_parameter_finish_choose_norm(
        cb: CallbackQuery,
        state: FSMContext,
        parameter_service: ParameterService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    data = await state.get_data()
    parameter_id: int = data['parameter_id']
    selected: list[str] = data['selected']

    new_norm_row: str = ';'.join(selected)

    parameter_dto = UpdateParameterDTO(norm_row=new_norm_row)

    parameter: Parameter = await parameter_service.update(item_id=parameter_id, item=parameter_dto)

    await cb.message.answer(text=f"Успешно изменена норма параметра <b>{parameter.name}</b>.\n"
                                 f"Текущая норма: <i>{parameter.norm_row}</i>",
                            parse_mode="HTML",
                            reply_markup=generate_admin_to_parameter_keyboard(parameter_id=parameter_id)
                            )
    await state.clear()


@router.message(StateFilter(ParameterEditStates.awaiting_new_norm_row))
async def admin_edit_parameter_awaiting_new_norm_row(
        msg: Message,
        state: FSMContext,
        parameter_service: ParameterService
):
    data = await state.get_data()
    parameter_id: int = data['parameter_id']

    res = await validate_norm_row(
        msg=msg,
        state=state,
        error_state=ParameterEditStates.awaiting_new_norm_row,
        norm_row=msg.text
    )
    if not res: return

    parameter_dto = UpdateParameterDTO(norm_row=msg.text)
    parameter: Parameter = await parameter_service.update(item_id=parameter_id, item=parameter_dto)

    keyboard = generate_admin_to_parameter_keyboard(parameter_id)
    await msg.answer(text=f"Успешно изменена норма для параметра <b>{parameter.name}</b>.\n"
                          f"Текущая норма: <i>{parameter.norm_row}</i>",
                     parse_mode="HTML",
                     reply_markup=keyboard
                     )
    await state.clear()


@router.callback_query(F.data.startswith("admin:parameter:edit:choice_open:"))
async def admin_edit_parameter_choice_open(
        cb: CallbackQuery,
        state: FSMContext,
        parameter_service: ParameterService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    parameter_id = int(cb.data.split(":")[-1])

    parameter: Parameter = await parameter_service.get_by_id(item_id=parameter_id)

    await state.update_data(
        parameter_id=parameter_id,
        choice=parameter.choice,
    )
    await state.set_state(ParameterEditStates.awaiting_new_choice)
    await cb.message.answer(text=f"Введите новые варианты ответов для параметра <b>{parameter.name}</b>.\n"
                                 f"Текущий выбор: <i>{parameter.choice}</i>",
                            parse_mode="HTML",
                            reply_markup=generate_admin_edit_parameter_cancel_keyboard(parameter_id=parameter_id))


@router.message(StateFilter(ParameterEditStates.awaiting_new_choice))
async def admin_edit_parameter_enter_new_choice(
        msg: Message,
        state: FSMContext
):
    data = await state.get_data()
    parameter_id: int = data['parameter_id']
    choice: str = data['choice']

    new_choice: str = msg.text

    pattern = re.compile(r"^[^;]+(;[^;]+)+$")
    if pattern.match(choice) is None:
        await msg.answer(text="Неверно введены варианты ответов! Используйте ';' для разделения вариантов.\n"
                                  "<i>Пример: яблоко;груша;слива</i>",
                         parse_mode="HTML",
                         reply_markup=generate_admin_edit_parameter_cancel_keyboard(parameter_id=parameter_id))
        await state.set_state(ParameterRegistrationStates.awaiting_choose_row)
        return

    if set(new_choice.split(';')) == set(choice.split(';')):
        await msg.answer(text="Введены те же варианты ответов! Попробуйте ещё раз или нажмите <i>Отмена</i>",
                         parse_mode="HTML",
                         reply_markup=generate_admin_edit_parameter_cancel_keyboard(parameter_id=parameter_id))
        await state.set_state(ParameterEditStates.awaiting_new_choice)
        return

    await state.update_data(choice=new_choice, selected=[])
    await state.set_state(ParameterEditStates.choosing_new_choice_norm)

    await msg.answer(text="Выберите норму.",
                     reply_markup=generate_admin_edit_parameter_norm_choose_keyboard(
                         parameter_id=parameter_id,
                         choices=new_choice,
                         selected=[]
                     ))


@router.callback_query(F.data.startswith("admin:parameter:edit:norm:choice:"),
                       StateFilter(ParameterEditStates.choosing_new_choice_norm))
async def admin_edit_parameter_choosing_new_choice_norm(
        cb: CallbackQuery,
        state: FSMContext
):
    await choosing_new_norm(
        cb=cb,
        state=state,
        next_state=ParameterEditStates.choosing_new_choice_norm
    )


@router.callback_query(F.data == "admin:parameter:edit:finish_choose_norms",
                       StateFilter(ParameterEditStates.choosing_new_choice_norm))
async def admin_edit_parameter_finish_choose_norms_choice(
        cb: CallbackQuery,
        state: FSMContext,
        parameter_service: ParameterService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    data = await state.get_data()

    parameter_id: int = data['parameter_id']
    choice: str = data['choice']
    selected: list[str] = data['selected']

    new_norm: str = ';'.join(selected)

    parameter_dto = UpdateParameterDTO(norm_row=new_norm, choice=choice)
    parameter: Parameter = await parameter_service.update(item_id=parameter_id, item=parameter_dto)

    await cb.message.answer(text=f"Успешно изменён параметр <b>{parameter.name}</b>.\n"
                                 f"Текущий выбор: <i>{parameter.choice}</i>\n"
                                 f"Текущая норма: <i>{new_norm}</i>",
                            parse_mode="HTML",
                            reply_markup=generate_admin_to_parameter_keyboard(parameter_id=parameter_id))
    await state.clear()


async def validate_norm_row(
        msg: Message,
        state: FSMContext,
        error_state: State,
        norm_row: str
) -> tuple[str, Norm] | None:
    data = await state.get_data()
    rule: str = data['rule']

    norm: Norm | None = await is_norm_correct(rule, norm_row, msg, state)
    if norm is None:
        return None

    if not norm.can_parse(norm_row):
        await msg.answer(text=f"Неподходящая норма для выбранного правила <b>{rule}</b>.\n", parse_mode="HTML")
        await state.set_state(error_state)
        return None

    return rule, norm


async def is_norm_correct(
        rule: str,
        norm_row: str,
        msg: Message,
        state: FSMContext,
) -> Norm | None:
    try:
        norm: Norm = NormFactory.create(rule, norm_row)
        return norm
    except ValueError:
        await msg.answer(
            text=(
                f"Критическая ошибка: для правила <b>{rule}</b> нет валидатора нормы.\n"
                f"Вернитесь в главное меню и пересоздайте параметр.\n"
                f"<i>Если ошибка повторится - обратитесь в службу поддержки.</i>"
            ),
            parse_mode="HTML",
            reply_markup=generate_admin_to_main_keyboard()
        )
        await state.clear()
        return None


async def choosing_new_norm(
        cb: CallbackQuery,
        state: FSMContext,
        next_state: State
):
    data = await state.get_data()
    parameter_id: int = data['parameter_id']
    choice: str = data['choice']
    selected: list[str] = data['selected']

    norm: str = cb.data.split(":")[-1]

    if norm in selected:
        selected.remove(norm)
    else:
        selected.append(norm)

    await state.update_data(selected=selected)
    await cb.message.edit_reply_markup(
        reply_markup=generate_admin_edit_parameter_norm_choose_keyboard(
            parameter_id=parameter_id,
            choices=choice,
            selected=selected
        ))
    await state.set_state(next_state)


@router.callback_query(F.data.startswith("admin:parameter:edit:instruction:"))
async def admin_edit_parameter_instruction_open(
        cb: CallbackQuery,
        state: FSMContext,
        parameter_service: ParameterService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    parameter_id: int = int(cb.data.split(":")[-1])
    parameter: Parameter = await parameter_service.get_by_id(item_id=parameter_id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✏️Очистить инструкцию", callback_data=f"admin:parameter:edit:clean_instruction")],
            generate_admin_edit_parameter_cancel_keyboard(parameter_id=parameter_id).inline_keyboard[0]
        ]
    )

    await cb.message.answer(text=f"Введите инструкцию для параметра <b>{parameter.name}</b>.\n"
                                 f"Текущая инструкция: <i>{parameter.instruction}</i>",
                            parse_mode="HTML",
                            reply_markup=keyboard)
    await state.update_data(parameter_id=parameter_id, instruction=parameter.instruction)
    await state.set_state(ParameterEditStates.awaiting_new_instruction)


@router.message(StateFilter(ParameterEditStates.awaiting_new_instruction))
async def admin_edit_parameter_enter_instruction(
        msg: Message,
        state: FSMContext,
        parameter_service: ParameterService
):
    data = await state.get_data()
    parameter_id: int = data['parameter_id']
    current_instruction: str = data['instruction']

    new_instruction: str = msg.text
    if current_instruction == new_instruction:
        await msg.answer(text="Введена та же инструкция! Введите новую или нажмите <i>Отмена</i>",
                         parse_mode="HTML",
                         reply_markup=generate_admin_edit_parameter_cancel_keyboard(parameter_id=parameter_id)
                         )
        await state.set_state(ParameterEditStates.awaiting_new_instruction)
        return

    parameter_dto = UpdateParameterDTO(instruction=new_instruction)
    parameter: Parameter = await parameter_service.update(item_id=parameter_id, item=parameter_dto)

    await msg.answer(text=f"Инструкция для параметра <b>{parameter.name}</b> успешно изменена.\n"
                          f"Текущая инструкция: <i>{parameter.instruction}</i>",
                     parse_mode="HTML",
                     reply_markup=generate_admin_to_parameter_keyboard(parameter_id=parameter_id))


@router.callback_query(F.data == "admin:parameter:edit:clean_instruction")
async def admin_edit_parameter_clean_instruction(
        cb: CallbackQuery,
        state: FSMContext,
        parameter_service: ParameterService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    data = await state.get_data()
    parameter_id: int = data['parameter_id']

    new_instruction: str = ""

    parameter_dto = UpdateParameterDTO(instruction=new_instruction)
    parameter: Parameter = await parameter_service.update(item_id=parameter_id, item=parameter_dto)

    await cb.message.answer(text=f"Инструкция параметра <b>{parameter.name}</b> успешно очищена.",
                            parse_mode="HTML",
                            reply_markup=generate_admin_to_parameter_keyboard(parameter_id=parameter_id))


@router.callback_query(F.data.startswith("admin:parameter:delete"))
async def admin_delete_parameter(
        cb: CallbackQuery,
        parameter_service: ParameterService
):
    await cb.answer()
    await safe_message_delete(cb.message)

    parameter_id: int = int(cb.data.split(":")[-1])
    parameter: Parameter = await parameter_service.get_by_id(item_id=parameter_id)

    await parameter_service.delete(parameter)

    await cb.message.answer(text="Параметр успешно удалён.",
                            reply_markup=InlineKeyboardMarkup(
                                inline_keyboard=[
                                    [InlineKeyboardButton(text="🔙Ко всем параметрам",
                                                          callback_data="admin:all_parameters")]
                                ]
                            ))