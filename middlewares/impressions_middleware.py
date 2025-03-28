import logging
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject, User, InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database.action_data_class import DataInteraction
from utils.translator.translator import Translator


class ImpressionsMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user: User = data.get('event_from_user')
        session: DataInteraction = data.get('session')
        translator: Translator = data.get('translator')
        for impression in await session.get_impressions():
            if not await session.check_user_impression(impression.id, user.id):
                form = await session.get_form(user.id)
                if not form:
                    return await handler(event, data)
                if (
                    ((form.male in [translator[male] for male in impression.male]) if impression.male else True)
                    and ((form.age in range(impression.min_age, impression.max_age)) if impression.min_age and impression.max_age else True)
                    and ((form.city in [city for city in impression.city]) if impression.city else True)
                    and ((form.profession == impression.profession) if impression.profession else True)
                    and ((form.education in [translator[education] for education in impression.education]) if impression.education else True)
                    and ((form.income in [translator[income] for income in impression.income]) if impression.income else True)
                    and ((form.religion in [translator[religion] for religion in impression.religion]) if impression.religion else True)
                    #  отдельное условие
                    and ((form.children_count == impression.children_count if isinstance(impression.children_count, int)
                    else form.children_count == translator[impression.children_count])
                    if impression.children_count else True)
                    #  конец условия
                    and ((form.children in [translator[children] for children in impression.children]) if impression.children else True)
                ):
                    keyboard = None
                    if impression.keyboard:
                        keyboard = [InlineKeyboardButton(text=i[0], url=i[1]) for i in impression.keyboard]
                    bot: Bot = data.get('bot')
                    await bot.copy_message(
                        chat_id=user.id,
                        from_chat_id=impression.from_chat_id,
                        message_id=impression.message_id,
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard]) if keyboard else None
                    )
                    await session.add_user_impression(impression.id, user.id, True)
                else:
                    await session.add_user_impression(impression.id, user.id, False)
        return await handler(event, data)
