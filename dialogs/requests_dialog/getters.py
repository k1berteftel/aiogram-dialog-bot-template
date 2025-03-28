from aiogram.types import CallbackQuery, User, Message, ContentType, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.schedulers import del_message
from utils.build_ids import get_random_id
from utils.translator.translator import Translator
from utils.text_utils import get_age_text
from database.action_data_class import DataInteraction
from config_data.config import load_config, Config
from states.state_groups import requestsSG


async def start_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['requests'],
        'my_requests': translator['my_requests_button'],
        'alien_requests': translator['alien_requests_button']
    }


async def my_pager(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('next'):
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') + 1
    else:
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') - 1
    await dialog_manager.switch_to(requestsSG.my_requests)


async def back(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['page'] = None
    await dialog_manager.switch_to(requestsSG.start)


async def my_requests_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = dialog_manager.middleware_data.get('translator')
    forms = await session.get_my_requests(event_from_user.id)
    page = dialog_manager.dialog_data.get('page')
    if page is None:
        page = 0
        dialog_manager.dialog_data['page'] = page
    not_first = True
    not_last = True
    if page == 0:
        not_first = False
    if len(forms) - 1 <= page:
        not_last = False
    media = None
    if forms:
        form = await session.get_form(forms[page].receiver)
        user = await session.get_user(form.user_id)
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
        if form.photos:
            photo = MediaId(file_id=form.photos.split(' ')[0])
            media = MediaAttachment(file_id=photo, type=ContentType.PHOTO)
    else:
        text = translator['no_my_requests']
    return {
        'media': media,
        'text': text,
        'form': bool(forms),
        'cancel': translator['cancel_my_request_button'],
        'complain': translator['complain_request_button'],
        'back': translator['back'],
        'not_first': not_first,
        'not_last': not_last
    }


async def cancel_my_request(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = dialog_manager.middleware_data.get('translator')
    page = dialog_manager.dialog_data.get('page')
    forms = await session.get_my_requests(clb.from_user.id)
    form = forms[page]
    await session.del_request(form.id)
    await clb.answer(translator['success_cancel_my_request'])


async def complain_my_request(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = dialog_manager.middleware_data.get('translator')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    page = dialog_manager.dialog_data.get('page')
    forms = await session.get_my_requests(msg.from_user.id)
    form = forms[page]
    await session.add_complain(msg.from_user.id, form.receiver, text)
    message = (await msg.answer(translator['success_complain_add']))
    job_id = get_random_id()
    scheduler.add_job(
        del_message,
        'interval',
        args=[message, scheduler, job_id],
        seconds=7,
        id=job_id
    )
    await dialog_manager.switch_to(requestsSG.my_requests)


async def my_request_complain_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['get_complain'],
        'back': translator['back']
    }


async def alien_pager(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('next'):
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') + 1
    else:
        dialog_manager.dialog_data['page'] = dialog_manager.dialog_data.get('page') - 1
    await dialog_manager.switch_to(requestsSG.alien_requests)


async def confirm_alien_request(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = dialog_manager.middleware_data.get('translator')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    page = dialog_manager.dialog_data.get('page')
    forms = await session.get_requests_to_my(clb.from_user.id)
    sender_form = forms[page]
    form = await session.get_form(clb.from_user.id)
    user = await session.get_user(clb.from_user.id)
    if form.male == translator['men_button']:
        if user.vip:
            price = 5
            if user.tokens < 5:
                message = await clb.message.answer(translator['no_tokens_warning'])
                job_id = get_random_id()
                scheduler.add_job(
                    del_message,
                    'interval',
                    args=[message, scheduler, job_id],
                    seconds=7,
                    id=job_id
                )
                return
        else:
            price = 10
            if user.tokens < 10:
                message = await clb.message.answer(translator['no_tokens_warning'])
                job_id = get_random_id()
                scheduler.add_job(
                    del_message,
                    'interval',
                    args=[message, scheduler, job_id],
                    seconds=7,
                    id=job_id
                )
                return
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
    sender = await session.get_user(forms[page].sender)
    send_form = await session.get_form(sender.user_id)
    if send_form.male == translator['men_button']:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=translator['get_contact_button'], callback_data=f'get_contact_{clb.from_user.id}')]]
        )
        await clb.bot.send_message(text=translator['success_apply_request'].format(form=text), reply_markup=keyboard, chat_id=sender.user_id)
        message = await clb.message.answer(translator['success_men_send'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        await session.del_request(sender_form.id)
    else:
        await clb.message.answer(translator['success_my_request'].format(username=sender.username))
        await clb.bot.send_message(
            chat_id=sender.user_id,
            text=translator['success_alien_request'].format(form=text, username=clb.from_user.username)
        )
        await session.update_tokens(clb.from_user.id, -price)
        await session.del_request(sender_form.id)


async def alien_requests_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = dialog_manager.middleware_data.get('translator')
    forms = await session.get_requests_to_my(event_from_user.id)
    page = dialog_manager.dialog_data.get('page')
    if page is None:
        page = 0
        dialog_manager.dialog_data['page'] = page
    not_first = True
    not_last = True
    if page == 0:
        not_first = False
    if len(forms) - 1 <= page:
        not_last = False
    media = None
    if forms:
        form = await session.get_form(forms[page].sender)
        user = await session.get_user(form.user_id)
        text = translator['form'].format(
                name=form.name,
                age=form.age,
                male=form.male,
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
        if form.photos:
            photo = MediaId(file_id=form.photos.split(' ')[0])
            media = MediaAttachment(file_id=photo, type=ContentType.PHOTO)
    else:
        text = translator['no_alien_requests']
    return {
        'media': media,
        'text': text,
        'form': bool(forms),
        'confirm': translator['confirm_alien_request_button'],
        'decline': translator['decline_alien_request_button'],
        'complain': translator['complain_request_button'],
        'back': translator['back'],
        'not_first': not_first,
        'not_last': not_last
    }


async def decline_alien_request(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = dialog_manager.middleware_data.get('translator')
    page = dialog_manager.dialog_data.get('page')
    forms = await session.get_requests_to_my(clb.from_user.id)
    form = forms[page]
    await session.del_request(form.id)
    await clb.answer(translator['success_decline_alien_request'])


async def complain_alien_request(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = dialog_manager.middleware_data.get('translator')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    page = dialog_manager.dialog_data.get('page')
    forms = await session.get_requests_to_my(msg.from_user.id)
    form = forms[page]
    await session.add_complain(msg.from_user.id, form.sender, text)
    message = await msg.answer(translator['success_complain_add'])
    job_id = get_random_id()
    scheduler.add_job(
        del_message,
        'interval',
        args=[message, scheduler, job_id],
        seconds=7,
        id=job_id
    )
    await dialog_manager.switch_to(requestsSG.alien_requests)


async def alien_request_complain_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['get_complain'],
        'back': translator['back']
    }
