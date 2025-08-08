from aiogram.fsm.state import StatesGroup, State


class ParameterRegistrationStates(StatesGroup):
    awaiting_parameter_name = State()
    choosing_roles = State()
    choosing_rule = State()
    awaiting_choose_row = State()
    choosing_norm = State()
    awaiting_norm_row = State()
    awaiting_instruction = State()