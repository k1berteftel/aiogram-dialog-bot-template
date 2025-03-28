from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, User, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput

from utils.translator.translator import Translator
from database.action_data_class import DataInteraction
from states.state_groups import infoSG


async def start_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    return {
        'text': translator['info'],
        'rules': translator['rules_button'],
        'info': translator['info_dialog_button']
    }


async def rules_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    return {
        'text': translator['rules'],
        'back': translator['back']
    }


async def info_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    form = await session.get_form(event_from_user.id)
    text = translator['women_info'] if form.male == translator['women_button'] else translator['men_info']
    return {
        'text': text,
        'back': translator['back']
    }