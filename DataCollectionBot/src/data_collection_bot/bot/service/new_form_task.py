from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage

from src.data_collection_bot import UserService, User, Role, Parameter, Roles
from src.data_collection_bot.bot.states import PollStates
from src.data_collection_bot.bot.keyboards import user_keyboard


async def daily_params_start_init(
        bot: Bot,
        storage: RedisStorage,
        user_service: UserService,
):
    print("start daily params")
    print(bot)
    print(storage)
    print(user_service)
    print("Type in bad method ", type(user_service.model))
    '''
    from sqlalchemy import text

    async with user_service.repository.session as session:  # или с твоей session
        result = await session.execute(text("SELECT * FROM users"))
        rows = result.fetchall()
        print("RAW SQL USERS:", rows)
        count_result = await session.execute(text("SELECT COUNT(*) FROM users"))
        count = count_result.scalar()
        print("RAW SQL USERS COUNT:", count)
    '''
    users: list[User] = await user_service.get_all()
    print("Всего пользователей:", len(users))
    # for user in users:
    #     print(user.telegram_id)
    #     if user.role.name == Roles.ADMIN.value: continue
    #     print("Go", user.telegram_id)
    #     state: FSMContext = FSMContext(
    #         storage=storage,
    #         key=StorageKey(bot_id=bot.id,
    #                        chat_id=user.telegram_id,
    #                        user_id=user.telegram_id
    #                        )
    #     )
    #     await daily_params_start(bot=bot, state=state, user=user)
    #     print("success daily params", user.telegram_id)


async def daily_params_start(
        bot: Bot,
        state: FSMContext,
        user: User
):
    role: Role = user.role
    print(role.name)
    parameters: list[Parameter] = role.parameters
    print(parameters[0].name)
    await state.update_data(parameters=parameters, user=user, index=0, answers=dict())
    await ask_next_param(bot=bot, state=state)
    print("success ask", user.telegram_id)


async def ask_next_param(
        bot: Bot,
        state: FSMContext
):
    data = await state.get_data()
    parameters: list[Parameter] = data['parameters']
    user: User = data['user']
    index: int = data['index']

    if index >= len(parameters):
        await bot.send_message(chat_id=user.telegram_id, text="Спасибо! Вы заполнили все параметры!")
        await state.clear()
        return

    text: str = await prepare_text(parameters=parameters, index=index)

    if parameters[index].choice is None:
        try:
            await bot.send_message(chat_id=user.telegram_id, text=text, parse_mode='html')
            await state.set_state(PollStates.waiting_answer)
            return
        except Exception as e:
            import traceback
            print("Error sending text:", user.telegram_id, e)
            traceback.print_exc()

    try:
        keyboard = user_keyboard(choice=parameters[index].choice.split(';'))
        await bot.send_message(chat_id=user.telegram_id, text=text, parse_mode='html', reply_markup=keyboard)
        await state.set_state(PollStates.waiting_answer)
    except Exception as e:
        import traceback
        print("Error sending text:", user.telegram_id, e)
        traceback.print_exc()



async def prepare_text(parameters: list[Parameter], index: int) -> str:
    parameter: Parameter = parameters[index]
    name = parameter.name
    rule = parameter.rule
    choice = parameter.choice
    instruction = parameter.instruction

    text: str = f'{'Введите' if choice is None else 'Выберите'}, пожалуйста, <b>{name}</b>\n'
    if instruction is not None:
        text += f'\nДля этого {instruction}'
    text += f'<i>Введённое значение должно соответствовать правилу: {rule}</i>'
    return text
