from datetime import datetime
from typing import Type

from aiogram import Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from src.data_collection_bot import (RoleService, UserService, Parameter, ValidatorFactory, Norm, Validator,
                                     NormFactory, RecordService)
from src.data_collection_bot.bot.states import PollStates
from src.data_collection_bot.bot.service import ask_next_param
from src.data_collection_bot.bot.utils import safe_message_delete

router = Router()


def get_router() -> Router:
    return router


@router.message(StateFilter(PollStates.waiting_answer))
async def user_enter_message(
        message: Message,
        state: FSMContext,
        user_service: UserService,
        role_service: RoleService,
        record_service: RecordService,
        bot: Bot
):
    data = await state.get_data()
    role_id: int = data.get("role_id")
    index: int = data.get("index")
    answers: dict = data.get("answers")

    answer: str = message.text

    parameter: Parameter = (await role_service.get_parameters_by_role_id(role_id))[index]

    validator_cls: Type[Validator] = ValidatorFactory.get_class(parameter.rule)

    if not validator_cls.validate(answer) or parameter.choice is not None:
        await message.answer(text=f"Введено неверное значение для параметра <b>{parameter.name}</b>.\n"
                                  f"Введите <i>{parameter.rule}</i>", parse_mode="html")
        await ask_next_param(
            bot=bot,
            state=state,
            user_service=user_service,
            role_service=role_service,
            record_service=record_service,
        )
        return

    await save_answer(
        bot=bot,
        state=state,
        user_service=user_service,
        role_service=role_service,
        record_service=record_service,
        answers=answers,
        index=index,
        answer=answer,
        parameter=parameter
    )


@router.callback_query(F.data.startswith('answer:'), StateFilter(PollStates.waiting_answer))
async def user_answer_callback(
        callback_query: CallbackQuery,
        state: FSMContext,
        user_service: UserService,
        role_service: RoleService,
        record_service: RecordService,
        bot: Bot
):
    await callback_query.answer()
    await safe_message_delete(callback_query.message)

    data = await state.get_data()
    role_id: int = data.get("role_id")
    index: int = data.get("index")
    answers: dict = data.get("answers")

    answer: str = callback_query.data.split(":")[-1]
    await callback_query.message.answer(text=f'Выбран ответ <b>{answer}</b>.', parse_mode="html")

    parameter: Parameter = (await role_service.get_parameters_by_role_id(role_id))[index]

    await save_answer(
        bot=bot,
        state=state,
        user_service=user_service,
        role_service=role_service,
        record_service=record_service,
        answers=answers,
        index=index,
        answer=answer,
        parameter=parameter
    )



async def save_answer(
        bot: Bot,
        state: FSMContext,
        user_service: UserService,
        role_service: RoleService,
        record_service: RecordService,
        answers: dict,
        index: int,
        answer: str,
        parameter: Parameter,
):
    norm: Norm = NormFactory.create(parameter.rule, parameter.norm_row)

    record: dict = {
        "answer": answer,
        "is_norm": norm.is_norm(answer),
        "date": datetime.now().strftime("%Y-%m-%d"),
    }

    answers["answers"][parameter.name] = record

    index += 1
    await state.update_data(answers=answers, index=index)

    await ask_next_param(
        bot=bot,
        state=state,
        user_service=user_service,
        role_service=role_service,
        record_service=record_service,
    )