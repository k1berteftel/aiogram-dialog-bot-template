from aiogram.types import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url, Cancel
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.targeting_dialog import getters
from states.state_groups import targetingSG


targeting_dialog = Dialog(
    Window(
        Format('Действующие параметры:\n{params}\nПодходящее кол-во пользователей: {count}'),
        Group(
            SwitchTo(Const('Пол'), id='get_male_switcher', state=targetingSG.get_male),
            Button(Const('Сбросить пол'), id='male_throw', on_click=getters.throw_off),
            SwitchTo(Const('Возраст'), id='get_age_range_switcher', state=targetingSG.get_age_range),
            Button(Const('Сбросить возраст'), id='age_throw', on_click=getters.throw_off),
            SwitchTo(Const('Город'), id='get_city_switcher', state=targetingSG.get_city),
            Button(Const('Сбросить город'), id='city_throw', on_click=getters.throw_off),
            SwitchTo(Const('Профессия'), id='get_profession_switcher', state=targetingSG.get_profession),
            Button(Const('Сбросить профессия'), id='profession_throw', on_click=getters.throw_off),
            SwitchTo(Const('Образование'), id='get_education_switcher', state=targetingSG.get_education),
            Button(Const('Сбросить образование'), id='education_throw', on_click=getters.throw_off),
            SwitchTo(Const('Доход'), id='get_income_switcher', state=targetingSG.get_income),
            Button(Const('Сбросить доход'), id='income_throw', on_click=getters.throw_off),
            SwitchTo(Const('Религия'), id='get_religion_switcher', state=targetingSG.get_religion),
            Button(Const('Сбросить религию'), id='religion_throw', on_click=getters.throw_off),
            SwitchTo(Const('Семейное положение'), id='get_family_switcher', state=targetingSG.get_family),
            Button(Const('Сбросить семейное положение'), id='family_throw', on_click=getters.throw_off),
            SwitchTo(Const('Кол-во детей'), id='get_children_count_switcher', state=targetingSG.get_children_count),
            Button(Const('Сбросить кол-во детей'), id='children_count_throw', on_click=getters.throw_off),
            SwitchTo(Const('Отношение по детям'), id='get_children_switcher', state=targetingSG.get_children),
            Button(Const('Сбросить отношение по детям'), id='children_throw', on_click=getters.throw_off),
            width=2
        ),
        Button(Const('Начать таргетированную рассылку'), id='get_mail_switcher', on_click=getters.get_male_switcher),
        Cancel(Const('Назад'), id='close_dialog'),
        getter=getters.create_impression_menu_getter,
        state=targetingSG.menu
    ),
    Window(
        Const('Введите диапозон возрастов вашей целевой аудитории в данном формате \n<em>'
              '20-35</em>'),
        TextInput(
            id='get_age',
            on_success=getters.get_age_range
        ),
        SwitchTo(Const('Назад'), id='back_menu', state=targetingSG.menu),
        state=targetingSG.get_age_range
    ),
    Window(
        Const('Укажите пол'),
        Column(
            Button(Format('{men}Мужчина'), id='men_choose', on_click=getters.choose_male),
            Button(Format('{women}Женщина'), id='women_choose', on_click=getters.choose_male),
        ),
        SwitchTo(Const('Назад'), id='back_menu', state=targetingSG.menu),
        getter=getters.get_male_getter,
        state=targetingSG.get_male
    ),
    Window(
        Const('Введите название города или несколько городов через абзац, '
              'например чтобы добавить несколько городов напишите так:\nМосква\nПитер\nи так далее..'),
        TextInput(
            id='get_city',
            on_success=getters.get_city
        ),
        SwitchTo(Const('Назад'), id='back_menu', state=targetingSG.menu),
        state=targetingSG.get_city
    ),
    Window(
        Const('Введите название профессии или несколько профессий разделенных абзацом, '
              'н-р:\nповар\nкосметолог\nи так далее..'),
        TextInput(
            id='get_profession',
            on_success=getters.get_profession
        ),
        SwitchTo(Const('Назад'), id='back_menu', state=targetingSG.menu),
        state=targetingSG.get_profession
    ),
    Window(
        Const('Укажите уровень образования'),
        Column(
            Button(Format('{leaning}Еще учусь'), id='leaning_education_choose', on_click=getters.choose_education),
            Button(Format('{eleven}11 классов'), id='eleven_education_choose', on_click=getters.choose_education),
            Button(Format('{average}Среднее специальное'), id='average_education_choose',
                   on_click=getters.choose_education),
            Button(Format('{higher}Высшее'), id='higher_education_choose', on_click=getters.choose_education),
        ),
        SwitchTo(Const('Назад'), id='back_menu', state=targetingSG.menu),
        getter=getters.get_education_getter,
        state=targetingSG.get_education
    ),
    Window(
        Const('Укажите уровень дохода'),
        Column(
            Button(Format('{no}Нет дохода'), id='no_income_choose', on_click=getters.choose_income),
            Button(Format('{low}Низкий'), id='low_income_choose', on_click=getters.choose_income),
            Button(Format('{average}Средний'), id='average_income_choose', on_click=getters.choose_income),
            Button(Format('{high}Высокий'), id='high_income_choose', on_click=getters.choose_income),
        ),
        SwitchTo(Const('Назад'), id='back_menu', state=targetingSG.menu),
        getter=getters.get_income_getter,
        state=targetingSG.get_income
    ),
    Window(
        Const('Укажите религию'),
        Column(
            Button(Format('{christian}Христианство'), id='christian_choose', on_click=getters.choose_religion),
            Button(Format('{islam}Ислам'), id='islam_choose', on_click=getters.choose_religion),
            Button(Format('{another}Другое'), id='another_choose', on_click=getters.choose_religion),
        ),
        SwitchTo(Const('Назад'), id='back_menu', state=targetingSG.menu),
        getter=getters.get_religion_getter,
        state=targetingSG.get_religion
    ),
    Window(
        Const('Укажите семейное положение'),
        Column(
            Button(Format('{no}Никогда не был(а) в браке'), id='no_family_choose', on_click=getters.choose_family),
            Button(Format('{divorce}Разведен'), id='divorce_family_choose', on_click=getters.choose_family),
            Button(Format('{widow}Вдовец/вдова'), id='widow_family_choose', on_click=getters.choose_family),
        ),
        SwitchTo(Const('Назад'), id='back_menu', state=targetingSG.menu),
        getter=getters.get_family_getter,
        state=targetingSG.get_family
    ),
    Window(
        Const('Укажите кол-во детей'),
        TextInput(
            id='get_children_count',
            on_success=getters.get_children_count
        ),
        Button(Const('Нет детей'), id='no_children_count_choose', on_click=getters.choose_children_count),
        SwitchTo(Const('Назад'), id='back_menu', state=targetingSG.menu),
        state=targetingSG.get_children_count
    ),
    Window(
        Const('Укажите отношение к заводу детей'),
        Column(
            Button(Format('{yes}Да'), id='yes_children_choose', on_click=getters.choose_children),
            Button(Format('{no}Нет'), id='no_children_choose', on_click=getters.choose_children),
            Button(Format('{maybe}Возможно'), id='maybe_children_choose', on_click=getters.choose_children),
            Button(Format('{not}Не важно'), id='not_matter_children_choose', on_click=getters.choose_children),
        ),
        SwitchTo(Const('Назад'), id='back_menu', state=targetingSG.menu),
        getter=getters.get_children_getter,
        state=targetingSG.get_children
    ),
    Window(
        Const('Введите сообщение которое вы хотели бы разослать'),
        MessageInput(
            content_types=ContentType.ANY,
            func=getters.get_mail
        ),
        SwitchTo(Const('Назад'), id='back', state=targetingSG.menu),
        state=targetingSG.get_mail
    ),
    Window(
        Const('Введите время через которое сообщение должно удалиться у всех пользователей\n'
              'Введите текст в формате: 02:30 (2 часа: 30 минут)'),
        TextInput(
            id='get_time',
            on_success=getters.get_time
        ),
        SwitchTo(Const('Продолжить без автоудаления'), id='get_keyboard_switcher', state=targetingSG.get_keyboard),
        SwitchTo(Const('Назад'), id='back_get_mail', state=targetingSG.get_mail),
        state=targetingSG.get_time
    ),
    Window(
        Const('Введите кнопки которые будут крепиться к рассылаемому сообщению\n'
              'Введите кнопки в формате:\n кнопка1 - ссылка1\nкнопка2 - ссылка2'),
        TextInput(
            id='get_mail_keyboard',
            on_success=getters.get_mail_keyboard
        ),
        SwitchTo(Const('Продолжить без кнопок'), id='confirm_mail_switcher', state=targetingSG.confirm_mail),
        SwitchTo(Const('Назад'), id='back_get_time', state=targetingSG.get_time),
        state=targetingSG.get_keyboard
    ),
    Window(
        Const('Вы подтверждаете рассылку сообщения'),
        Row(
            Button(Const('Да'), id='start_malling', on_click=getters.start_malling),
            Button(Const('Нет'), id='cancel_malling', on_click=getters.cancel_malling),
        ),
        SwitchTo(Const('Назад'), id='back_get_keyboard', state=targetingSG.get_keyboard),
        state=targetingSG.confirm_mail
    ),

)