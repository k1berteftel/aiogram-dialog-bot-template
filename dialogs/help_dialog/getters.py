from aiogram.types import CallbackQuery, User, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput

from utils.translator.translator import Translator
from database.action_data_class import DataInteraction
from config_data.config import load_config, Config
from states.state_groups import searchSG


async def start_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['help'],
        'contact': translator['contact_button']
    }
