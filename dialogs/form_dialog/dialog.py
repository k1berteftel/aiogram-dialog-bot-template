from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.form_dialog import getters

from states.state_groups import formSG


form_dialog = Dialog(
    Window(
        Format('{text}'),
        TextInput(
            id='get_name',
            on_success=getters.get_name
        ),
        getter=getters.get_name_getter,
        state=formSG.get_name
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_age',
            on_success=getters.get_age
        ),
        SwitchTo(Format('{back}'), id='back_get_name', state=formSG.get_name),
        getter=getters.get_age_getter,
        state=formSG.get_age
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{men}'), id='men_choose', on_click=getters.choose_male),
            Button(Format('{women}'), id='women_choose', on_click=getters.choose_male),
        ),
        SwitchTo(Format('{back}'), id='back_get_age', state=formSG.get_age),
        getter=getters.get_male_getter,
        state=formSG.get_male
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_city',
            on_success=getters.get_city
        ),
        SwitchTo(Format('{back}'), id='back_get_male', state=formSG.get_male),
        getter=getters.get_city_getter,
        state=formSG.get_city
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_profession',
            on_success=getters.get_profession
        ),
        SwitchTo(Format('{back}'), id='back_get_city', state=formSG.get_city),
        getter=getters.get_profession_getter,
        state=formSG.get_profession
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{leaning}'), id='leaning_education_choose', on_click=getters.choose_education),
            Button(Format('{eleven}'), id='eleven_education_choose', on_click=getters.choose_education),
            Button(Format('{average}'), id='average_education_choose', on_click=getters.choose_education),
            Button(Format('{higher}'), id='higher_education_choose', on_click=getters.choose_education),
        ),
        SwitchTo(Format('{back}'), id='back_get_profession', state=formSG.get_profession),
        getter=getters.get_education_getter,
        state=formSG.get_education
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{no}'), id='no_income_choose', on_click=getters.choose_income),
            Button(Format('{low}'), id='low_income_choose', on_click=getters.choose_income),
            Button(Format('{average}'), id='average_income_choose', on_click=getters.choose_income),
            Button(Format('{high}'), id='high_income_choose', on_click=getters.choose_income),
        ),
        SwitchTo(Format('{back}'), id='back_get_education', state=formSG.get_education),
        getter=getters.get_income_getter,
        state=formSG.get_income
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_plans',
            on_success=getters.get_description
        ),
        SwitchTo(Format('{back}'), id='back_get_income', state=formSG.get_income),
        getter=getters.get_description_getter,
        state=formSG.get_description
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{islam}'), id='islam_choose', on_click=getters.choose_religion),
            Button(Format('{christian}'), id='christian_choose', on_click=getters.choose_religion),
            Button(Format('{another}'), id='another_choose', on_click=getters.choose_religion),
        ),
        SwitchTo(Format('{back}'), id='back_get_plans', state=formSG.get_description),
        getter=getters.get_religion_getter,
        state=formSG.get_religion
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{yes}'), id='yes_second_choose', on_click=getters.choose_second_wife),
            Button(Format('{no}'), id='no_second_choose', on_click=getters.choose_second_wife),
        ),
        SwitchTo(Format('{back}'), id='back_get_religion', state=formSG.get_religion),
        getter=getters.get_second_wife_getter,
        state=formSG.get_second_wife
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{family}'), id='family_choose', on_click=getters.choose_family, when='family'),
            Button(Format('{no_family}'), id='no_family_choose', on_click=getters.choose_family),
            Button(Format('{divorce_family}'), id='divorce_family_choose', on_click=getters.choose_family),
            Button(Format('{widow_family}'), id='widow_family_choose', on_click=getters.choose_family),
        ),
        SwitchTo(Format('{back}'), id='back_get_religion', state=formSG.get_religion),
        getter=getters.get_family_getter,
        state=formSG.get_family
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_children_count',
            on_success=getters.get_children_count
        ),
        Button(Format('{no_children}'), id='no_children_count_choose', on_click=getters.choose_children_count),
        SwitchTo(Format('{back}'), id='back_get_family', state=formSG.get_family),
        getter=getters.get_children_count_getter,
        state=formSG.get_children_count
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{yes}'), id='yes_children_choose', on_click=getters.choose_children),
            Button(Format('{no}'), id='no_children_choose', on_click=getters.choose_children),
            Button(Format('{maybe}'), id='maybe_children_choose', on_click=getters.choose_children),
            Button(Format('{not_matter}'), id='not_matter_children_choose', on_click=getters.choose_children),
        ),
        SwitchTo(Format('{back}'), id='back_get_children_count', state=formSG.get_children_count),
        getter=getters.get_children_getter,
        state=formSG.get_children
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{yes}'), id='yes_leave_choose', on_click=getters.choose_leave),
            Button(Format('{no}'), id='no_leave_choose', on_click=getters.choose_leave),
        ),
        SwitchTo(Format('{back}'), id='back_get_children', state=formSG.get_children),
        getter=getters.get_leave_getter,
        state=formSG.get_leave
    ),
    Window(
        Format('{text}'),
        MessageInput(
            content_types=ContentType.PHOTO,
            func=getters.get_photo_1
        ),
        SwitchTo(Format('{back}'), id='back_get_leave', state=formSG.get_leave),
        Button(Format('{skip}'), id='skip_get_photos', on_click=getters.skip_get_photos),
        getter=getters.get_photo_1_getter,
        state=formSG.get_photo_1
    ),
    Window(
        Format('{text}'),
        MessageInput(
            content_types=ContentType.PHOTO,
            func=getters.get_photo_2
        ),
        SwitchTo(Format('{back}'), id='back_get_photo_1', state=formSG.get_photo_1),
        Button(Format('{skip}'), id='skip_get_photos', on_click=getters.skip_get_photos),
        getter=getters.get_photo_2_getter,
        state=formSG.get_photo_2
    ),
    Window(
        Format('{text}'),
        MessageInput(
            content_types=ContentType.PHOTO,
            func=getters.get_photo_3
        ),
        SwitchTo(Format('{back}'), id='back_get_photo_2', state=formSG.get_photo_2),
        Button(Format('{skip}'), id='skip_get_photos', on_click=getters.skip_get_photos),
        getter=getters.get_photo_3_getter,
        state=formSG.get_photo_3
    )
)