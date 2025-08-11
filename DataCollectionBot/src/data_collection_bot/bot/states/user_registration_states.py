from aiogram.fsm.state import StatesGroup, State


class UserRegistrationStates(StatesGroup):
    awaiting_first_name = State()
    awaiting_last_name = State()
    awaiting_birthday = State()