from aiogram.types import Message, InlineKeyboardMarkup

from src.data_collection_bot.bot.keyboards.admin import generate_admin_start_keyboard


async def admin_start(msg: Message):
    text: str = "👋Привет, админ!"
    keyboard: InlineKeyboardMarkup = generate_admin_start_keyboard()
    await msg.answer(text=text)
    text = "Выбери, что ты хочешь сделать."
    await msg.answer(text=text, reply_markup=keyboard)


async def admin_has_registered(msg: Message):
    keyboard: InlineKeyboardMarkup = generate_admin_start_keyboard()
    text = "Выбери следующее действие."
    await msg.answer(text=text, reply_markup=keyboard)