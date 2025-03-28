import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, User, Message
from utils.translator import Translator as create_translator
from utils.translator.translator import Translator


class SupportMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        user: User = data.get('event_from_user')
        if not user.username:
            translator: Translator = create_translator('ru')
            bot: Bot = data.get('bot')
            await bot.send_message(
                chat_id=user.id,
                text=translator['no_username_warning']
            )
            return
        if isinstance(event, Message):
            if event.chat.id != user.id:
                return
        return await handler(event, data)