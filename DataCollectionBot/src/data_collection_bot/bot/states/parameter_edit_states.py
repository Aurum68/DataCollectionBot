from aiogram.fsm.state import StatesGroup, State


class ParameterEditStates(StatesGroup):
    awaiting_new_name = State()
    choosing_new_roles = State()

    choosing_new_rule = State()
    awaiting_new_choice_rule = State()
    choosing_new_choice_norm_rule = State()
    awaiting_new_norm_row_rule = State()

    choosing_new_norm = State()
    awaiting_new_norm_row = State()

    awaiting_new_choice = State()
    choosing_new_choice_norm = State()