from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url, Cancel
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.language_dialog import getters
from states.state_groups import languagesSG


language_dialog = Dialog(
    Window(
        Format('{text}'),
        Column(
            Button(Const('🇷🇺Русский'), id='ru_language_switcher', on_click=getters.language_toggle),
            Button(Const('🇬🇧English'), id='en_language_switcher', on_click=getters.language_toggle),
            Button(Const("🇺🇿O'zbek tili"), id='uz_language_switcher', on_click=getters.language_toggle),
            Button(Const('🇹🇷Türk'), id='tr_language_switcher', on_click=getters.language_toggle),
            Button(Const('🇹🇯Тоҷикӣ'), id='tg_language_switcher', on_click=getters.language_toggle),
        ),
        Cancel(Format('{back}'), id='close_dialog', when='not_start'),
        getter=getters.start_getter,
        state=languagesSG.start
    )
)
