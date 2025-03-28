from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.user_dialog.getters import start_getter

from states.state_groups import startSG, adminSG

user_dialog = Dialog(
    Window(
        Const('Приветственный текст'),
        Column(
            Start(Const('Админ панель'), id='admin', state=adminSG.start, when='admin')
        ),
        getter=start_getter,
        state=startSG.start
    )
)