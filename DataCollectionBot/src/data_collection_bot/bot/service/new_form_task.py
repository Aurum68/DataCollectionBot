from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage

from src. data_collection_bot. database. db_config import AsyncSessionLocal

from src.data_collection_bot import UserService, User, Role, Parameter, Roles, RoleService, Rules, RecordService, \
    CreateRecordDTO, UserRepository, RoleRepository, ParameterRepository, RecordRepository
from src.data_collection_bot.bot.states import PollStates
from src.data_collection_bot.bot.keyboards import user_keyboard
from src.data_collection_bot.exel import save_records

'''
async def daily_params_start_init(
        bot: Bot,
        storage: RedisStorage,
        user_service: UserService,
        role_service: RoleService,
        record_service: RecordService,
): 
    user_ids: list[int] = [user.id for user in (await user_service.get_all())]
    for user_id in user_ids:
        user: User = await user_service.get_by_id(user_id)
        print(user.telegram_id)
        if user.role.name == Roles.ADMIN.value: continue
        state: FSMContext = FSMContext(
            storage=storage,
            key=StorageKey(bot_id=bot.id,
                           chat_id=user.telegram_id,
                           user_id=user.telegram_id
                           )
        )
        await daily_params_start(
            bot=bot,
            state=state,
            user=user,
            user_service=user_service,
            role_service=role_service,
            record_service=record_service,
        )
'''
async def daily_params_start_init(
        bot: Bot,
        storage: RedisStorage,
):
    async with AsyncSessionLocal() as session:
        user_repository = UserRepository(session)
        user_service = UserService(user_repository)

        role_repository = RoleRepository(session)
        parameter_repository = ParameterRepository(session)
        role_service = RoleService(role_repository, parameter_repository)

        record_repository = RecordRepository(session)
        record_service = RecordService(record_repository)

        user_ids: list[int] = [user.id for user in (await user_service.get_all())]
        for user_id in user_ids:
            user: User = await user_service.get_by_id(user_id)
            print(user.telegram_id)
            if user.role.name == Roles.ADMIN.value: continue
            state: FSMContext = FSMContext(
                storage=storage,
                key=StorageKey(bot_id=bot.id,
                               chat_id=user.telegram_id,
                               user_id=user.telegram_id
                               )
            )
            await daily_params_start(
                bot=bot,
                state=state,
                user=user,
                user_service=user_service,
                role_service=role_service,
                record_service=record_service,
            )


async def daily_params_start(
        bot: Bot,
        state: FSMContext,
        user: User,
        user_service: UserService,
        role_service: RoleService,
        record_service: RecordService,
):
    role: Role = user.role
    print(role.name)
    await state.update_data(user_id=user.id, role_id=role.id, index=0, answers={"user_id": user.id, 'answers': {}})
    await ask_next_param(
        bot=bot,
        state=state,
        user_service=user_service,
        role_service=role_service,
        record_service=record_service,
    )


async def ask_next_param(
        bot: Bot,
        state: FSMContext,
        user_service: UserService,
        role_service: RoleService,
        record_service: RecordService
):
    data = await state.get_data()
    user_id: int = data['user_id']
    role_id: int = data['role_id']
    index: int = data['index']

    user: User = await user_service.get_by_id(user_id)
    parameters: list[Parameter] = await role_service.get_parameters_by_role_id(role_id)

    if index >= len(parameters):
        await bot.send_message(chat_id=user.telegram_id, text="Спасибо! Вы заполнили все параметры!")
        await save_record(
            data=data,
            user_service=user_service,
            record_service=record_service,
        )
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


async def save_record(
        data: dict,
        user_service: UserService,
        record_service: RecordService,
):
    answers: dict = data['answers']
    user_id: int = answers['user_id']
    answers_dict: dict = answers['answers']

    record_dto: CreateRecordDTO = CreateRecordDTO(user_id=user_id, data=answers_dict)
    await record_service.create(record_dto)

    user: User = await user_service.get_by_id(user_id)

    await save_records(user_pseudonym=user.pseudonym, answers=answers_dict)


async def prepare_text(parameters: list[Parameter], index: int) -> str:
    parameter: Parameter = parameters[index]
    name = parameter.name
    rule = parameter.rule
    choice = parameter.choice
    instruction = parameter.instruction

    text: str = f'{'Введите' if choice is None else 'Выберите'}, пожалуйста, <b>{name}</b>\n'
    if instruction is not None:
        text += f'\nДля этого {instruction}'
    if rule != Rules.CHOOSE.name:
        text += f'<i>Введённое значение должно соответствовать правилу: {Rules[rule].value}</i>'
    return text
