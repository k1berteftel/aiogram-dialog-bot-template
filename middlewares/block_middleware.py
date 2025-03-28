import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, User
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select
from cachetools import TTLCache

from database.action_data_class import DataInteraction
from database.model import UsersTable
from config_data.config import load_config, Config


config: Config = load_config()
logger = logging.getLogger(__name__)


class BlockMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.cache = TTLCache(
            maxsize=1000,
            ttl=60 * 60 * 12,  # 12 часов
        )

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        event_from_user: User = data.get('event_from_user')
        if event_from_user.id not in self.cache:
            sessions: async_sessionmaker = data.get('_session')
            async with sessions() as session:
                user = await session.scalar(select(UsersTable).where(UsersTable.user_id == event_from_user.id))
                if not user:
                    data['cache'] = self.cache
                    return await handler(event, data)
                self.cache[event_from_user.id] = user
        else:
            user = self.cache.get(event_from_user.id)
        if user.block:
            return
        data['cache'] = self.cache
        return await handler(event, data)