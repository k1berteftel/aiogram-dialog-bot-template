from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.search_dialog import getters

from states.state_groups import searchSG


search_dialog = Dialog(
    Window(
        Format('{text}'),
        Column(
            Button(Format('{search}'), id='start_search', on_click=getters.search_forms),
            Button(Format('{filter}'), id='filter_menu', on_click=getters.filter_menu_switcher),
        ),
        getter=getters.start_getter,
        state=searchSG.start
    ),
    Window(
        Format('{text}'),
        Column(
            SwitchTo(Format('{age}'), id='get_age_switcher', state=searchSG.get_age),
            SwitchTo(Format('{city}'), id='get_city_switcher', state=searchSG.get_city),
            SwitchTo(Format('{family}'), id='get_family_switcher', state=searchSG.get_family),
            SwitchTo(Format('{children}'), id='get_children_switcher', state=searchSG.get_children),
            SwitchTo(Format('{religion}'), id='get_religion_switcher', state=searchSG.get_religion),
        ),
        Button(Format('{search}'), id='start_filter_forms', on_click=getters.filter_forms),
        SwitchTo(Format('{back}'), id='back', state=searchSG.start),
        getter=getters.filter_menu_getter,
        state=searchSG.filter_menu
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_age',
            on_success=getters.get_age
        ),
        SwitchTo(Format('{back}'), id='back_filter_menu', state=searchSG.filter_menu),
        getter=getters.get_age_getter,
        state=searchSG.get_age
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_city',
            on_success=getters.get_city
        ),
        SwitchTo(Format('{back}'), id='back_filter_menu', state=searchSG.filter_menu),
        getter=getters.get_city_getter,
        state=searchSG.get_city
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{family}'), id='family_choose', on_click=getters.choose_family, when='family'),
            Button(Format('{no_family}'), id='no_family_choose', on_click=getters.choose_family),
            Button(Format('{divorce_family}'), id='divorce_family_choose', on_click=getters.choose_family),
            Button(Format('{widow_family}'), id='widow_family_choose', on_click=getters.choose_family),
        ),
        SwitchTo(Format('{back}'), id='back_filter_menu', state=searchSG.filter_menu),
        getter=getters.get_family_getter,
        state=searchSG.get_family
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{yes}'), id='yes_children_choose', on_click=getters.choose_children),
            Button(Format('{no}'), id='no_children_choose', on_click=getters.choose_children),
            Button(Format('{maybe}'), id='maybe_children_choose', on_click=getters.choose_children),
            Button(Format('{not_matter}'), id='not_matter_children_choose', on_click=getters.choose_children),
        ),
        SwitchTo(Format('{back}'), id='back_filter_menu', state=searchSG.filter_menu),
        getter=getters.get_children_getter,
        state=searchSG.get_children
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{christian}'), id='christian_choose', on_click=getters.choose_religion),
            Button(Format('{islam}'), id='islam_choose', on_click=getters.choose_religion),
            Button(Format('{another}'), id='another_choose', on_click=getters.choose_religion),
        ),
        SwitchTo(Format('{back}'), id='back_filter_menu', state=searchSG.filter_menu),
        getter=getters.get_religion_getter,
        state=searchSG.get_religion
    ),
)