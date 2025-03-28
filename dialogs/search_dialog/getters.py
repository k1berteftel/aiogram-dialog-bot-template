from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, User, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram.utils.media_group import MediaGroupBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.translator.translator import Translator
from utils.build_ids import get_random_id
from utils.schedulers import del_message
from utils.text_utils import get_age_text
from keyboard.keyboards import get_search_keyboard
from database.action_data_class import DataInteraction
from config_data.config import load_config, Config
from states.state_groups import searchSG


async def start_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['search'],
        'search': translator['search_button'],
        'filter': translator['filter_button'],
    }


async def search_forms(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = dialog_manager.middleware_data.get('translator')
    state: FSMContext = dialog_manager.middleware_data.get('state')
    forms = await session.filter_forms(clb.from_user.id)
    if not forms:
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        message = await clb.message.answer(translator['form_error'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        await dialog_manager.switch_to(searchSG.start, show_mode=ShowMode.DELETE_AND_SEND)
        return
    form = await session.get_form_by_id(forms[0])
    forms.pop(0)
    user = await session.get_user(form.user_id)
    await state.set_state(searchSG.search_menu)
    await state.set_data({'forms': forms})
    text = translator['form'].format(
            name=form.name,
            male=form.male,
            age=form.age,
            age_text=get_age_text(form.age),
            city=form.city,
            profession=form.profession,
            education=form.education,
            income=form.income,
            description=form.description,
            religion=form.religion,
            family=form.family,
            children_count=form.children_count,
            children=form.children,
            leave=form.leave,
            vip='✅' if user.vip else '❌'
        )
    builder: MediaGroupBuilder = MediaGroupBuilder()
    if form.photos:
        for photo in form.photos:
            builder.add_photo(media=photo)
        await clb.message.answer_media_group(media=builder.build())
    await clb.message.answer(
        text=text,
        reply_markup=get_search_keyboard(translator, form_user_id=form.user_id)
    )
    await session.add_watch(clb.from_user.id, form.id)
    await dialog_manager.done()
    await clb.message.delete()


async def filter_forms(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = dialog_manager.middleware_data.get('translator')
    state: FSMContext = dialog_manager.middleware_data.get('state')
    age = dialog_manager.dialog_data.get('age')
    city = dialog_manager.dialog_data.get('city')
    family = dialog_manager.dialog_data.get('family')
    children = dialog_manager.dialog_data.get('children')
    religion = dialog_manager.dialog_data.get('religion')
    user_form = await session.get_form(clb.from_user.id)
    forms = await session.filter_forms_by_params(
        clb.from_user.id,
        age=age,
        city=city,
        family=family,
        children=children,
        religion=religion,
    )
    if not forms:
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        message = await clb.message.answer(translator['form_error'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        await dialog_manager.switch_to(searchSG.filter_menu, show_mode=ShowMode.DELETE_AND_SEND)
        return
    form = await session.get_form_by_id(forms[0])
    forms.pop(0)
    user = await session.get_user(form.user_id)
    await state.set_state(searchSG.search_menu)
    await state.set_data({'forms': forms})
    text = translator['form'].format(
            name=form.name,
            male=form.male,
            age=form.age,
            age_text=get_age_text(form.age),
            city=form.city,
            profession=form.profession,
            education=form.education,
            income=form.income,
            description=form.description,
            religion=form.religion,
            family=form.family,
            children_count=form.children_count,
            children=form.children,
            leave=form.leave,
            vip='✅' if user.vip else '❌'
        )

    builder: MediaGroupBuilder = MediaGroupBuilder()
    if form.photos:
        for photo in form.photos.split(' '):
            builder.add_photo(photo)
        await clb.message.answer_media_group(media=builder.build())
    await clb.message.answer(
        text=text,
        reply_markup=get_search_keyboard(translator, form_user_id=form.user_id)
    )
    await session.add_watch(clb.from_user.id, form.id)
    await dialog_manager.done()
    await clb.message.delete()


async def filter_menu_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    age = dialog_manager.dialog_data.get('age')
    city = dialog_manager.dialog_data.get('city')
    family = dialog_manager.dialog_data.get('family')
    children = dialog_manager.dialog_data.get('children')
    religion = dialog_manager.dialog_data.get('religion')
    params = ''
    if age:
        params += translator['filter_age_text'].format(min_age=age[0], max_age=age[1]) + '\n'
    if city:
        params += translator['filter_city_text'].format(text=city) + '\n'
    if family:
        params += translator['filter_family_text'].format(text=family) + '\n'
    if children:
        params += translator['filter_children_text'].format(text=children) + '\n'
    if religion:
        params += translator['filter_religion_text'].format(text=religion)
    return {
        'text': translator['filter'].format(params=params),
        'city': translator['filter_city_button'],
        'age': translator['filter_age_button'],
        'family': translator['filter_family_button'],
        'children': translator['filter_children_button'],
        'religion': translator['filter_religion_button'],
        'search': translator['start_filter_button'],
        'back': translator['back']
    }


async def filter_menu_switcher(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(clb.from_user.id)
    if not user.vip:
        await clb.answer(translator['vip_filter_only_warning'])
        return
    await dialog_manager.switch_to(searchSG.filter_menu)


async def get_age(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        age = [int(i) for i in text.split('-')]
    except Exception as err:
        translator: Translator = dialog_manager.middleware_data.get('translator')
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        message = await msg.answer(text=translator['add_age_range_error'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        return
    if age[0] <= 17 or age[1] >= 99 or len(age) != 2:
        translator: Translator = dialog_manager.middleware_data.get('translator')
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        message = await msg.answer(text=translator['add_age_range_error'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        return
    dialog_manager.dialog_data['age'] = age
    await msg.delete()
    await dialog_manager.switch_to(searchSG.filter_menu, show_mode=ShowMode.EDIT)


async def get_age_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_age_range'],
        'back': translator['back']
    }


async def get_city_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_city'],
        'back': translator['back']
    }


async def get_city(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if len(text) > 30:
        translator: Translator = dialog_manager.middleware_data.get('translator')
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        message = await msg.answer(text=translator['add_city_error'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        return
    dialog_manager.dialog_data['city'] = text[0].upper() + text[1::]
    await msg.delete()
    await dialog_manager.switch_to(searchSG.filter_menu, show_mode=ShowMode.EDIT)


async def get_family_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    form = await session.get_form(event_from_user.id)
    return {
        'text': translator['get_family'],
        'family': translator['family_button'] if form.male == translator['men_button'] and form.religion == translator['add_religion_islam_button'] else False,
        'no_family': translator['no_family_button'],
        'divorce_family': translator['divorce_family_button'],
        'widow_family': translator['widow_family_button'],
        'back': translator['back']
    }


async def choose_family(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('no'):
        dialog_manager.dialog_data['family'] = clb.message.reply_markup.inline_keyboard[1][0].text
    elif clb.data.startswith('divorce'):
        dialog_manager.dialog_data['family'] = clb.message.reply_markup.inline_keyboard[2][0].text
    elif clb.data.startswith('family'):
        dialog_manager.dialog_data['family'] = clb.message.reply_markup.inline_keyboard[0][0].text
    else:
        dialog_manager.dialog_data['family'] = clb.message.reply_markup.inline_keyboard[3][0].text
    await dialog_manager.switch_to(searchSG.filter_menu, show_mode=ShowMode.EDIT)


async def get_children_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['get_children'],
        'yes': translator['add_children_yes_button'],
        'no': translator['add_children_no_button'],
        'maybe': translator['add_children_maybe_button'],
        'not_matter': translator['add_children_not_matter_button'],
        'back': translator['back']
    }


async def choose_children(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('yes'):
        # можно делать через widget
        dialog_manager.dialog_data['children'] = clb.message.reply_markup.inline_keyboard[0][0].text
    elif clb.data.startswith('no_'):
        dialog_manager.dialog_data['children'] = clb.message.reply_markup.inline_keyboard[1][0].text
    elif clb.data.startswith('maybe'):
        dialog_manager.dialog_data['children'] = clb.message.reply_markup.inline_keyboard[2][0].text
    else:
        dialog_manager.dialog_data['children'] = clb.message.reply_markup.inline_keyboard[3][0].text
    await dialog_manager.switch_to(searchSG.filter_menu, show_mode=ShowMode.EDIT)


async def get_religion_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['get_religion'],
        'christian': translator['add_religion_christian_button'],
        'islam': translator['add_religion_islam_button'],
        'another': translator['add_religion_another_button'],
        'back': translator['back']
    }


async def choose_religion(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    if clb.data.startswith('christian'):
        dialog_manager.dialog_data['religion'] = clb.message.reply_markup.inline_keyboard[0][0].text
    elif clb.data.startswith('islam'):
        dialog_manager.dialog_data['religion'] = clb.message.reply_markup.inline_keyboard[1][0].text
    else:
        dialog_manager.dialog_data['religion'] = clb.message.reply_markup.inline_keyboard[2][0].text
    await dialog_manager.switch_to(searchSG.filter_menu, show_mode=ShowMode.EDIT)
