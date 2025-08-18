from aiogram.fsm.state import StatesGroup, State


class PollStates(StatesGroup):
    waiting_answer = State()