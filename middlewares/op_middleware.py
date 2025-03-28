import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram_dialog import DialogManager, StartMode
from aiogram.types import TelegramObject, User
from database.action_data_class import DataInteraction
from states.state_groups import subSG

logger = logging.getLogger(__name__)


class OpMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        session: DataInteraction = data.get('session')
        channels = await session.get_op()
        if not channels:
            return await handler(event, data)
        bot: Bot = data.get('bot')
        dialog_manager: DialogManager = data.get('dialog_manager')
        user: User = data.get('event_from_user')
        for channel in channels:
            member = await bot.get_chat_member(chat_id=channel.chat_id, user_id=user.id)
            if member.status == 'left':
                await dialog_manager.start(subSG.start)
                return
        return await handler(event, data)