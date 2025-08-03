from aiogram import Bot
from aiogram.types import Message


async def user_start(msg: Message, bot: Bot):
    text: str = "👋Привет, юзер!"
    await bot.send_message(chat_id=msg.from_user.id, text=text)