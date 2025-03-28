from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.requests_dialog import getters

from states.state_groups import requestsSG


requests_dialog = Dialog(
    Window(
        Format('{text}'),
        Column(
            SwitchTo(Format('{my_requests}'), id='my_requests_switcher', state=requestsSG.my_requests),
            SwitchTo(Format('{alien_requests}'), id='alien_requests_switcher', state=requestsSG.alien_requests),
        ),
        getter=getters.start_getter,
        state=requestsSG.start
    ),
    Window(
        DynamicMedia('media', when='media'),
        Format('{text}'),
        Row(
            Button(Const('◀️'), id='previous_my_page', on_click=getters.my_pager, when='not_first'),
            Button(Const('▶️'), id='next_my_page', on_click=getters.my_pager, when='not_last'),
        ),
        Column(
            Button(Format('{cancel}'), id='cancel_my_request', on_click=getters.cancel_my_request, when='form'),
            SwitchTo(Format('{complain}'), id='complain_my_request', state=requestsSG.my_request_complain, when='form')
        ),
        Button(Format('{back}'), id='back', on_click=getters.back),
        getter=getters.my_requests_getter,
        state=requestsSG.my_requests
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_my_request_complain',
            on_success=getters.complain_my_request
        ),
        SwitchTo(Format('{back}'), id='back_my_request', state=requestsSG.my_requests),
        getter=getters.my_request_complain_getter,
        state=requestsSG.my_request_complain
    ),
    Window(
        DynamicMedia('media', when='media'),
        Format('{text}'),
        Row(
            Button(Const('◀️'), id='previous_alien_page', on_click=getters.alien_pager, when='not_first'),
            Button(Const('▶️'), id='next_alien_page', on_click=getters.alien_pager, when='not_last'),
        ),
        Row(
            Button(Format('{confirm}'), id='confirm_alien_request', on_click=getters.confirm_alien_request, when='form'),
            Button(Format('{decline}'), id='decline_alien_request', on_click=getters.decline_alien_request, when='form'),
        ),
        SwitchTo(Format('{complain}'), id='complain_alien_request', state=requestsSG.alien_request_complain, when='form'),
        Button(Format('{back}'), id='back', on_click=getters.back),
        getter=getters.alien_requests_getter,
        state=requestsSG.alien_requests
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_alien_request_complain',
            on_success=getters.complain_alien_request
        ),
        SwitchTo(Format('{back}'), id='back_alien_request', state=requestsSG.alien_requests),
        getter=getters.alien_request_complain_getter,
        state=requestsSG.alien_request_complain
    ),
)