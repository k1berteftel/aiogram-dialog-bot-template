from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.profile_dialog import getters

from states.state_groups import profileSG, balanceSG, formSG, languagesSG


profile_dialog = Dialog(
    Window(
        Format('{text}'),
        Column(
            SwitchTo(Format('{my_form}'), id='form_menu_switcher', state=profileSG.form_menu),
            Button(Format('{form_toggle}'), id='toggle_form_active', on_click=getters.toggle_form),
            Start(Format('{my_balance}'), id='start_balance_dialog', state=balanceSG.start),
            SwitchTo(Format('{refs}'), id='ref_menu_switcher', state=profileSG.ref_menu),
            Start(Format('{language}'), id='start_language_dialog', state=languagesSG.start),
        ),
        getter=getters.start_getter,
        state=profileSG.start
    ),
    Window(
        Format('{text}'),
        Column(
            Url(Format('{share}'), url=Format('http://t.me/share/url?url=https://t.me/Origandtocha_bot?start={user_id}')),
            SwitchTo(Format('{ref_static}'), id='ref_static_switcher', state=profileSG.ref_static)
        ),
        SwitchTo(Format('{back}'), id='back', state=profileSG.start),
        getter=getters.ref_menu_getter,
        state=profileSG.ref_menu
    ),
    Window(
        Format('{text}'),
        SwitchTo(Format('{back}'), id='back_ref_menu', state=profileSG.ref_menu),
        getter=getters.ref_static_getter,
        state=profileSG.ref_static
    ),
    Window(
        DynamicMedia('media', when='media'),
        Format('{text_1}:\n\n{text_2}'),
        Group(
            SwitchTo(Format('{name}'), id='change_name_switcher', state=profileSG.get_name),
            SwitchTo(Format('{age}'), id='change_age_switcher', state=profileSG.get_age),
            SwitchTo(Format('{male}'), id='change_male_switcher', state=profileSG.get_male),
            SwitchTo(Format('{city}'), id='change_city_switcher', state=profileSG.get_city),
            SwitchTo(Format('{profession}'), id='change_profession_switcher', state=profileSG.get_profession),
            SwitchTo(Format('{education}'), id='change_education_switcher', state=profileSG.get_education),
            SwitchTo(Format('{income}'), id='change_income_switcher', state=profileSG.get_income),
            SwitchTo(Format('{description}'), id='change_description_switcher', state=profileSG.get_description),
            SwitchTo(Format('{religion}'), id='change_religion_switcher', state=profileSG.get_religion),
            SwitchTo(Format('{second_wife}'), id='change_second_wife_switcher', state=profileSG.get_second_wife, when='second_wife'),
            SwitchTo(Format('{family}'), id='change_family_switcher', state=profileSG.get_family),
            SwitchTo(Format('{children_count}'), id='change_children_count_switcher', state=profileSG.get_children_count),
            SwitchTo(Format('{children}'), id='change_children_switcher', state=profileSG.get_children),
            SwitchTo(Format('{leave}'), id='change_leave_switcher', state=profileSG.get_leave),
            SwitchTo(Format('{photos}'), id='change_photos_switcher', state=profileSG.get_photo_1),
            width=2
        ),
        Column(
            Start(Format('{start_form}'), id='start_form_dialog', state=formSG.get_name),
            SwitchTo(Format('{back}'), id='back', state=profileSG.start),
        ),
        getter=getters.form_menu_getter,
        state=profileSG.form_menu
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_name',
            on_success=getters.get_name
        ),
        SwitchTo(Format('{back}'), id='back_form_menu', state=profileSG.form_menu),
        getter=getters.get_name_getter,
        state=profileSG.get_name
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_age',
            on_success=getters.get_age
        ),
        SwitchTo(Format('{back}'), id='back_form_menu', state=profileSG.form_menu),
        getter=getters.get_age_getter,
        state=profileSG.get_age
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{start_form}'), id='change_male', on_click=getters.choose_male),
        ),
        SwitchTo(Format('{back}'), id='back_form_menu', state=profileSG.form_menu),
        getter=getters.get_male_getter,
        state=profileSG.get_male
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_city',
            on_success=getters.get_city
        ),
        SwitchTo(Format('{back}'), id='back_form_menu', state=profileSG.form_menu),
        getter=getters.get_city_getter,
        state=profileSG.get_city
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_profession',
            on_success=getters.get_profession
        ),
        SwitchTo(Format('{back}'), id='back_form_menu', state=profileSG.form_menu),
        getter=getters.get_profession_getter,
        state=profileSG.get_profession
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{leaning}'), id='leaning_education_choose', on_click=getters.choose_education),
            Button(Format('{eleven}'), id='eleven_education_choose', on_click=getters.choose_education),
            Button(Format('{average}'), id='average_education_choose', on_click=getters.choose_education),
            Button(Format('{higher}'), id='higher_education_choose', on_click=getters.choose_education),
        ),
        SwitchTo(Format('{back}'), id='back_form_menu', state=profileSG.form_menu),
        getter=getters.get_education_getter,
        state=profileSG.get_education
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{no}'), id='no_income_choose', on_click=getters.choose_income),
            Button(Format('{low}'), id='low_income_choose', on_click=getters.choose_income),
            Button(Format('{average}'), id='average_income_choose', on_click=getters.choose_income),
            Button(Format('{high}'), id='high_income_choose', on_click=getters.choose_income),
        ),
        SwitchTo(Format('{back}'), id='back_form_menu', state=profileSG.form_menu),
        getter=getters.get_income_getter,
        state=profileSG.get_income
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_plans',
            on_success=getters.get_plans
        ),
        SwitchTo(Format('{back}'), id='back_form_menu', state=profileSG.form_menu),
        getter=getters.get_plans_getter,
        state=profileSG.get_description
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{christian}'), id='christian_choose', on_click=getters.choose_religion),
            Button(Format('{islam}'), id='islam_choose', on_click=getters.choose_religion),
            Button(Format('{another}'), id='another_choose', on_click=getters.choose_religion),
        ),
        SwitchTo(Format('{back}'), id='back_form_menu', state=profileSG.form_menu),
        getter=getters.get_religion_getter,
        state=profileSG.get_religion
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{yes}'), id='yes_second_choose', on_click=getters.choose_second_wife),
            Button(Format('{no}'), id='no_second_choose', on_click=getters.choose_second_wife),
        ),
        SwitchTo(Format('{back}'), id='back_form_menu', state=profileSG.form_menu),
        getter=getters.get_second_wife_getter,
        state=profileSG.get_second_wife
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{family}'), id='family_choose', on_click=getters.choose_family, when='family'),
            Button(Format('{no_family}'), id='no_family_choose', on_click=getters.choose_family),
            Button(Format('{divorce_family}'), id='divorce_family_choose', on_click=getters.choose_family),
            Button(Format('{widow_family}'), id='widow_family_choose', on_click=getters.choose_family),
        ),
        SwitchTo(Format('{back}'), id='back_form_menu', state=profileSG.form_menu),
        getter=getters.get_family_getter,
        state=profileSG.get_family
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_children_count',
            on_success=getters.get_children_count
        ),
        Button(Format('{no_children}'), id='no_children_count_choose', on_click=getters.choose_children_count),
        SwitchTo(Format('{back}'), id='back_form_menu', state=profileSG.form_menu),
        getter=getters.get_children_count_getter,
        state=profileSG.get_children_count
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{yes}'), id='yes_children_choose', on_click=getters.choose_children),
            Button(Format('{no}'), id='no_children_choose', on_click=getters.choose_children),
            Button(Format('{maybe}'), id='maybe_children_choose', on_click=getters.choose_children),
            Button(Format('{not_matter}'), id='not_matter_children_choose', on_click=getters.choose_children),
        ),
        SwitchTo(Format('{back}'), id='back_form_menu', state=profileSG.form_menu),
        getter=getters.get_children_getter,
        state=profileSG.get_children
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{yes}'), id='yes_leave_choose', on_click=getters.choose_leave),
            Button(Format('{no}'), id='no_leave_choose', on_click=getters.choose_leave),
        ),
        SwitchTo(Format('{back}'), id='back_form_menu', state=profileSG.form_menu),
        getter=getters.get_leave_getter,
        state=profileSG.get_leave
    ),
    Window(
        Format('{text}'),
        MessageInput(
            content_types=ContentType.PHOTO,
            func=getters.get_photo_1
        ),
        SwitchTo(Format('{back}'), id='back_form_menu', state=profileSG.form_menu),
        getter=getters.get_photo_1_getter,
        state=profileSG.get_photo_1
    ),
    Window(
        Format('{text}'),
        MessageInput(
            content_types=ContentType.PHOTO,
            func=getters.get_photo_2
        ),
        SwitchTo(Format('{back}'), id='back_get_photo_1', state=profileSG.get_photo_1),
        Button(Format('{skip}'), id='skip_get_photos', on_click=getters.skip_get_photos),
        getter=getters.get_photo_2_getter,
        state=profileSG.get_photo_2
    ),
    Window(
        Format('{text}'),
        MessageInput(
            content_types=ContentType.PHOTO,
            func=getters.get_photo_3
        ),
        SwitchTo(Format('{back}'), id='back_get_photo_2', state=profileSG.get_photo_2),
        Button(Format('{skip}'), id='skip_get_photos', on_click=getters.skip_get_photos),
        getter=getters.get_photo_3_getter,
        state=profileSG.get_photo_3
    )
)
