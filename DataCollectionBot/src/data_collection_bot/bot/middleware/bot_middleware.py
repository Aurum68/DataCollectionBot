from typing import Any, Dict, Callable, Awaitable

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject


class BotMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        self.bot = bot


    async def __call__(self,
                       handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                       event: TelegramObject,
                       data: Dict[str, Any]
                    )->Any:
        data['bot'] = self.bot
        return await handler(event, data)