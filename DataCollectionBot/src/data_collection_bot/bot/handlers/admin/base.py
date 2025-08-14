from typing import Optional

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from src.data_collection_bot.bot.keyboards.admin import generate_admin_start_keyboard
from src.data_collection_bot.bot.utils.helpers import safe_message_delete

router = Router()


def get_router() -> Router:
    return router


@router.callback_query(F.data == "admin:main")
async def admin_main(cb: CallbackQuery, state: Optional[FSMContext] = None):
    await cb.answer()
    await safe_message_delete(cb.message)

    if state:
        await state.clear()

    keyboard = generate_admin_start_keyboard()
    await cb.message.answer(text="Выбери следующее действие", reply_markup=keyboard)