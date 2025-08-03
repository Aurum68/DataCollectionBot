from aiogram import Bot
from aiogram.types import Message, InlineKeyboardMarkup

from src.data_collection_bot.bot.keyboards.admin import generate_admin_start_keyboard


async def admin_start(msg: Message, bot: Bot):
    text: str = "👋Привет, админ!"
    keyboard: InlineKeyboardMarkup = generate_admin_start_keyboard()
    await bot.send_message(chat_id=msg.from_user.id, text=text)
    text = "Выбери, что ты хочешь сделать."
    await bot.send_message(chat_id=msg.from_user.id, text=text, reply_markup=keyboard)