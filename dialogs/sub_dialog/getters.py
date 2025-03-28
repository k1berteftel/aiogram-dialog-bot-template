from aiogram import Bot
from aiogram.types import CallbackQuery, User, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.build_ids import get_random_id
from utils.schedulers import del_message
from utils.translator.translator import Translator
from database.action_data_class import DataInteraction


async def sub_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = dialog_manager.middleware_data.get('translator')
    categories = await session.get_op()
    buttons = []
    count = 0
    for button in categories:
        buttons.append((button.name, button.link, count))
        count += 1
    return {
        'text': translator['check_sub'],
        'items': buttons,
        'check_sub': translator['check_sub_button']
    }


async def check_sub(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    translator: Translator = dialog_manager.middleware_data.get('translator')
    channels = await session.get_op()
    for channel in channels:
        member = await bot.get_chat_member(chat_id=channel.chat_id, user_id=clb.from_user.id)
        if member.status == 'left':
            await clb.answer(translator['check_sub_warning'])
            return
    message = await clb.message.answer(translator['check_sub_success'])
    job_id = get_random_id()
    scheduler.add_job(
        del_message,
        'interval',
        args=[message, scheduler, job_id],
        seconds=7,
        id=job_id
    )

    await dialog_manager.done()
    await clb.message.delete()