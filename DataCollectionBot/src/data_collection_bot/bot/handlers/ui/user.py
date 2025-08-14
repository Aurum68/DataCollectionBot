import re
from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.data_collection_bot import UserService, User, UpdateUserDTO
from src.data_collection_bot.bot.states import UserRegistrationStates


router = Router()


def get_router() -> Router:
    return router


async def user_start(
        msg: Message,
        state: FSMContext
):
    await msg.answer(text="👋Здравствуйте! Я бот для сбора медицинских данных.\n"
                          "Каждый день в 8.00 я буду просить Вас заполнять медицинские показатели.")
    await msg.answer(text="Перед началом работы пройдите, пожалуйста, короткую форму регистрации.\n"
                          "Введите, пожалуйста, своё настоящее имя (имя ребёнка, если Вы родитель)")
    await state.set_state(UserRegistrationStates.awaiting_first_name)
    await state.update_data(user_tg_id=msg.from_user.id)


@router.message(StateFilter(UserRegistrationStates.awaiting_first_name))
async def user_enter_first_name(msg: Message, state: FSMContext):
    first_name = msg.text
    await state.update_data(first_name=first_name)
    await state.set_state(UserRegistrationStates.awaiting_last_name)
    await msg.answer(text="Отлично! Теперь введите, пожалуйста, свою настоящую фамилию (фамилию ребёнка, если Вы родитель)")


@router.message(StateFilter(UserRegistrationStates.awaiting_last_name))
async def user_enter_last_name(msg: Message, state: FSMContext):
    last_name = msg.text
    await state.update_data(last_name=last_name)
    await state.set_state(UserRegistrationStates.awaiting_patronymic)
    await msg.answer(
        text="Класс! Теперь введите, пожалуйста, своё настоящее отчество (отчество ребёнка, если Вы родитель) ",
        parse_mode='html',
    )


@router.message(UserRegistrationStates.awaiting_patronymic)
async def user_enter_patronymic(msg: Message, state: FSMContext):
    patronymic = msg.text
    await state.update_data(patronymic=patronymic)
    await state.set_state(UserRegistrationStates.awaiting_birthday)
    await msg.answer(text="Супер! Теперь введите, пожалуйста, свою настоящую дату рождения (дату рождения ребёнка, если Вы родитель)\n"
                          "<i>Дату рождения введите в виде ДД.ММ.ГГГГ. Пример: 23.07.2006</i>", parse_mode="HTML")


@router.message(StateFilter(UserRegistrationStates.awaiting_birthday))
async def user_enter_birthday(msg: Message, state: FSMContext, user_service: UserService):
    birthday = msg.text

    if not check_birthday(birthday):
        await msg.answer(text="неверный формат даты или такой даты не существует. Попробуйте ещё раз.\n"
                              "<i>Дату рождения введите в виде ДД.ММ.ГГГГ. Пример: 23.07.2006</i>", parse_mode="HTML")
        await state.set_state(UserRegistrationStates.awaiting_birthday)
        return

    bd: datetime = datetime.strptime(birthday, "%d.%m.%Y")

    data = await state.get_data()
    user_tg_id = data.get("user_tg_id")
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    patronymic = data.get("patronymic")

    user: User = await user_service.get_user_by_telegram_id(user_tg_id)

    user_dto = UpdateUserDTO(first_name=first_name, last_name=last_name, patronymic=patronymic, birthday=bd)

    await user_service.update(item_id=user.id, item=user_dto)

    await msg.answer(text="Вы успешно зарегистрированы!")


def check_birthday(birthday: str) -> bool:
    if not re.match(r'^\d{2}\.\d{2}\.\d{4}$', birthday):
        return False

    try:
        bd: datetime = datetime.strptime(birthday, '%d.%m.%Y')

        if bd.timestamp() > datetime.now(timezone.utc).timestamp():
            return False

        return True
    except ValueError:
        return False