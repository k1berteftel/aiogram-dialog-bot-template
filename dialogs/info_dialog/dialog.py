from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.info_dialog import getters

from states.state_groups import infoSG


info_dialog = Dialog(
    Window(
        Format('{text}'),
        Column(
            SwitchTo(Format('{rules}'), id='rules_switcher', state=infoSG.rules),
            SwitchTo(Format('{info}'), id='info_switcher', state=infoSG.info),
        ),
        getter=getters.start_getter,
        state=infoSG.start
    ),
    Window(
        Format('{text}'),
        SwitchTo(Format('{back}'), id='back', state=infoSG.start),
        getter=getters.rules_getter,
        state=infoSG.rules
    ),
    Window(
        Format('{text}'),
        SwitchTo(Format('{back}'), id='back', state=infoSG.start),
        getter=getters.info_getter,
        state=infoSG.info
    ),
)