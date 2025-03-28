import datetime
from aiogram import Bot
from aiogram.types import CallbackQuery, User, Message, ContentType, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.build_ids import get_random_id
from utils.text_utils import get_age_text
from utils.schedulers import send_messages
from utils.translator import Translator as create_translator
from utils.translator.translator import Translator, recreate_locales
from database.action_data_class import DataInteraction
from database.model import DeeplinksTable, AdminsTable
from config_data.config import load_config, Config
from states.state_groups import languagesSG


async def start_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    start = dialog_manager.start_data.get('start') if dialog_manager.start_data else False
    return {
        'text': translator['language'],
        'back': translator['back'],
        'not_start': not start
    }


async def language_toggle(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    locale = clb.data.split('_')[0]
    user = await session.get_user(clb.from_user.id)
    await session.set_locale(clb.from_user.id, locale)
    translator: Translator = create_translator(locale)
    start = dialog_manager.start_data.get('start') if dialog_manager.start_data else False
    await dialog_manager.done()
    if not await session.check_form(clb.from_user.id) or start:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=translator['confirm_terms_button'], callback_data='confirm_terms')]
            ]
        )
        await clb.message.answer(
            text=translator['start_message'],
            reply_markup=keyboard
        )
        await clb.message.delete()
        return

    form = await session.get_form(clb.from_user.id)
    form_dict = {
        'male': form.male,
        'education': form.education,
        'income': form.income,
        'religion': form.religion,
        'family': form.family,
        'leave': form.leave,
        'children': form.children
    }
    new_form_dict = recreate_locales(form_dict, user.locale, locale)
    print(new_form_dict)
    await session.update_form(clb.from_user.id, **new_form_dict)
