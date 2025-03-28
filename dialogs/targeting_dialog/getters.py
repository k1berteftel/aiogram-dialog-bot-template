import datetime
from aiogram import Bot
from aiogram.types import CallbackQuery, User, Message, ContentType, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.build_ids import get_random_id
from utils.text_utils import get_age_text
from utils.schedulers import send_messages_targeting
from utils.translator.translator import Translator, create_translator
from database.action_data_class import DataInteraction
from database.model import DeeplinksTable, AdminsTable
from config_data.config import load_config, Config
from states.state_groups import targetingSG


async def create_impression_menu_getter(dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = create_translator('ru')
    male: dict = dialog_manager.dialog_data.get('male')
    age = dialog_manager.dialog_data.get('age')
    city = dialog_manager.dialog_data.get('city')
    profession = dialog_manager.dialog_data.get('profession')
    education = dialog_manager.dialog_data.get('education')
    income = dialog_manager.dialog_data.get('income')
    religion = dialog_manager.dialog_data.get('religion')
    family = dialog_manager.dialog_data.get('family')
    children_count = dialog_manager.dialog_data.get('children_count')
    children = dialog_manager.dialog_data.get('children')

    users = await session.targeting_filter(
        male=male,
        age=age,
        city=city,
        profession=profession,
        education=education,
        income=income,
        religion=religion,
        family=family,
        children_count=children_count,
        children=children
    )
    dialog_manager.dialog_data['users'] = users

    params = ''
    if male is not None:
        params += 'Пол: '
        for i, v in male.items():
            params += f'{translator[v]}, ' if male[i] != v else translator[v]
        params += '\n'
    if age is not None:
        params += f'Возраст: {age[0]} до {age[1]}\n'
    if city is not None:
        params += f'Город: {"".join(f"{i}, " if i != city[-1] else f"{i}" for i in city)}\n'
    if profession is not None:
        params += f'Профессия: {"".join(f"{i}, " if i != profession[-1] else f"{i}" for i in profession)}\n'
    if education is not None:
        params += 'Образование: '
        for i, v in education.items():
            params += f'{translator[v]}, ' if education[i] != v else translator[v]
        params += '\n'
    if income is not None:
        params += 'Доход: '
        for i, v in income.items():
            params += f'{translator[v]}, ' if income[i] != v else translator[v]
        params += '\n'
    if religion is not None:
        params += 'Религия: '
        for i, v in religion.items():
            params += f'{translator[v]}, ' if religion[i] != v else translator[v]
        params += '\n'
    if family is not None:
        params += 'Семейное положение: '
        for i, v in family.items():
            params += f'{translator[v]}, ' if family[i] != v else translator[v]
        params += '\n'
    if children_count is not None:
        params += f'Кол-во детей: {children_count if isinstance(children_count, int) else translator[children_count]}\n'
    if children is not None:
        params += f'Отношение по детям: '
        for i, v in children.items():
            params += f'{translator[v]}, ' if children[i] != v else translator[v]
        params += '\n'

    return {
        'params': params,
        'count': len(users)
    }


async def get_age_range(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    await msg.delete()
    try:
        age = [int(i) for i in text.split('-')]
    except Exception:
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    if len(age) != 2:
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['age'] = age
    await dialog_manager.switch_to(targetingSG.menu)


async def choose_male(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    males: dict= dialog_manager.dialog_data.get('male')
    gender = clb.data.split('_')[0]
    if not males:
        males = {}
        males[gender] = gender + '_button'
    elif males.get(gender):
        del males[gender]
    else:
        males[gender] = gender + '_button'
    dialog_manager.dialog_data['male'] = males


async def get_male_getter(dialog_manager: DialogManager, **kwargs):
    males = dialog_manager.dialog_data.get('male')
    return {
        'men': '✅' if males and males.get('men') else '❌',
        'women': '✅' if males and males.get('women') else '❌'
    }


async def get_city(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    cities = dialog_manager.dialog_data.get('cities')
    if not cities:
        cities = text.split('\n')
    else:
        cities = cities.extend(text.split('\n'))
    dialog_manager.dialog_data['city'] = cities
    await dialog_manager.switch_to(targetingSG.menu)


async def get_profession(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    profession = dialog_manager.dialog_data.get('profession')
    if not profession:
        profession = text.split('\n')
    else:
        profession = profession.extend(text.split('\n'))
    dialog_manager.dialog_data['profession'] = profession
    await dialog_manager.switch_to(targetingSG.menu)


async def choose_education(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    education = dialog_manager.dialog_data.get('education')
    program = clb.data.split('_')[0]
    if not education:
        education = {}
        education[program] = 'add_education_' + clb.data.split('_')[0] + '_button'
    elif education.get(program):
        del education[program]
    else:
        education[program] = 'add_education_' + clb.data.split('_')[0] + '_button'
    dialog_manager.dialog_data['education'] = education


async def get_education_getter(dialog_manager: DialogManager, **kwargs):
    education = dialog_manager.dialog_data.get('education')
    return {
        'leaning': '✅' if education and education.get('leaning') else '❌',
        'eleven': '✅' if education and education.get('eleven') else '❌',
        'average': '✅' if education and education.get('average') else '❌',
        'higher': '✅' if education and education.get('higher') else '❌',
    }


async def choose_income(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    incomes = dialog_manager.dialog_data.get('income')
    income = clb.data.split('_')[0]
    if not incomes:
        incomes = {}
        incomes[income] = 'add_income_' + clb.data.split('_')[0] + '_button'
    elif incomes.get(income):
        del incomes[income]
    else:
        incomes[income] = 'add_income_' + clb.data.split('_')[0] + '_button'
    dialog_manager.dialog_data['income'] = incomes


async def get_income_getter(dialog_manager: DialogManager, **kwargs):
    income = dialog_manager.dialog_data.get('income')
    return {
        'no': '✅' if income and income.get('no') else '❌',
        'low': '✅' if income and income.get('low') else '❌',
        'average': '✅' if income and income.get('average') else '❌',
        'high': '✅' if income and income.get('high') else '❌',
    }


async def choose_religion(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    religions = dialog_manager.dialog_data.get('religion')
    religion = clb.data.split('_')[0]
    if not religions:
        religions = {}
        religions[religion] = 'add_religion_' + clb.data.split('_')[0] + '_button'
    elif religions.get(religion):
        del religions[religion]
    else:
        religions[religion] = 'add_religion_' + clb.data.split('_')[0] + '_button'
    dialog_manager.dialog_data['religion'] = religions


async def get_religion_getter(dialog_manager: DialogManager, **kwargs):
    religion = dialog_manager.dialog_data.get('religion')
    return {
        'christian': '✅' if religion and religion.get('christian') else '❌',
        'islam': '✅' if religion and religion.get('islam') else '❌',
        'another': '✅' if religion and religion.get('another') else '❌',
    }


async def choose_family(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    families = dialog_manager.dialog_data.get('family')
    family = clb.data.split('_')[0]
    if not families:
        families = {}
        families[family] = clb.data.split('_')[0] + '_family_button'
    elif families.get(family):
        del families[family]
    else:
        families[family] = clb.data.split('_')[0] + '_family_button'
    dialog_manager.dialog_data['family'] = families


async def get_family_getter(dialog_manager: DialogManager, **kwargs):
    family = dialog_manager.dialog_data.get('family')
    return {
        'no': '✅' if family and family.get('no') else '❌',
        'divorce': '✅' if family and family.get('divorce') else '❌',
        'widow': '✅' if family and family.get('widow') else '❌',
    }


async def get_children_count(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        children_count = int(text)
    except Exception:
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['children_count'] = children_count
    await dialog_manager.switch_to(targetingSG.menu)


async def choose_children_count(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['children_count'] = 'add_children_count_no_button'
    await dialog_manager.switch_to(targetingSG.menu)


async def choose_children(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    children = dialog_manager.dialog_data.get('children')
    mode = clb.data.split('_')[0]
    if not children:
        children = {}
        children[mode] = 'add_children_' + mode + '_button'
    elif children.get(mode):
        del children[mode]
    else:
        children[mode] = 'add_children_' + mode + '_button'
    dialog_manager.dialog_data['children'] = children


async def get_children_getter(dialog_manager: DialogManager, **kwargs):
    children = dialog_manager.dialog_data.get('children')
    return {
        'yes': '✅' if children and children.get('yes') else '❌',
        'no': '✅' if children and children.get('no') else '❌',
        'maybe': '✅' if children and children.get('maybe') else '❌',
        'not': '✅' if children and children.get('not') else '❌',
    }


async def throw_off(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    datas = clb.data.split('_')
    if datas[0] == 'children' and datas[1] == 'count':
        dialog_manager.dialog_data['children_count'] = None
        await dialog_manager.switch_to(targetingSG.menu)
        return
    dialog_manager.dialog_data[datas[0]] = None
    await dialog_manager.switch_to(targetingSG.menu)


async def get_male_switcher(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    users = dialog_manager.dialog_data.get('users')
    if len(users) < 1:
        await clb.answer('Недостаточно пользователей для таргетированной рассылки')
        return
    await dialog_manager.switch_to(targetingSG.get_mail)


async def get_mail(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    dialog_manager.dialog_data['message'] = [msg.message_id, msg.chat.id]
    await dialog_manager.switch_to(targetingSG.get_time)


async def get_time(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        times = text.split(':')
        time = datetime.time(hour=int(times[0]), minute=int(times[1]))
    except Exception as err:
        print(err)
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['time'] = [time.hour, time.minute]
    await dialog_manager.switch_to(targetingSG.get_keyboard)


async def get_mail_keyboard(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        buttons = text.split('\n')
        keyboard: list[list] = [[i.split('-')[0], i.split('-')[1]] for i in buttons]
    except Exception as err:
        print(err)
        await msg.answer('Вы ввели данные не в том формате, пожалуйста попробуйте снова')
        return
    dialog_manager.dialog_data['keyboard'] = keyboard
    await dialog_manager.switch_to(targetingSG.confirm_mail)


async def cancel_malling(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(targetingSG.menu)


async def start_malling(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    time = dialog_manager.dialog_data.get('time')
    message = dialog_manager.dialog_data.get('message')
    keyboard = dialog_manager.dialog_data.get('keyboard')
    if keyboard:
        keyboard = [InlineKeyboardButton(text=i[0], url=i[1]) for i in keyboard]
    users_id: list[int] = dialog_manager.dialog_data.get('users')
    users = []
    for user_id in users_id:
        users.append(await session.get_user(user_id))
    if not time:
        for user in users:
            try:
                await bot.copy_message(
                    chat_id=user.user_id,
                    from_chat_id=message[1],
                    message_id=message[0],
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[keyboard]) if keyboard else None
                )
                if user.active == 0:
                    await session.set_active(user.user_id, 1)
            except Exception as err:
                print(err)
                await session.set_active(user.user_id, 0)
        await clb.answer('Рассылка прошла успешно')
    else:
        today = datetime.datetime.today()
        date = datetime.datetime(year=today.year, month=today.month, day=today.day, hour=time[0], minute=time[1])
        scheduler.add_job(
            func=send_messages_targeting,
            args=[users, bot, session, InlineKeyboardMarkup(inline_keyboard=[keyboard]) if keyboard else None, message],
            next_run_time=date
        )
        await clb.answer('Рассылка была успешно отложена')
    dialog_manager.dialog_data.clear()
    await dialog_manager.switch_to(targetingSG.menu)

