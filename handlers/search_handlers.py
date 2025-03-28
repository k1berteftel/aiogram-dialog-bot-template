from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram_dialog import DialogManager, StartMode
from aiogram.utils.media_group import MediaGroupBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from utils.build_ids import get_random_id
from utils.schedulers import del_message
from keyboard.keyboards import get_search_keyboard
from utils.text_utils import get_age_text
from database.action_data_class import DataInteraction
from states.state_groups import searchSG
from utils.translator import Translator


search_router = Router()


@search_router.callback_query(F.data == 'next')
async def next_form(clb: CallbackQuery, state: FSMContext, translator: Translator, session: DataInteraction, scheduler: AsyncIOScheduler):
    forms = (await state.get_data()).get('forms')
    if not forms:
        forms = await session.filter_forms(user_id=clb.from_user.id)
        if not forms:
            message = await clb.message.answer(translator['form_error'])
            job_id = get_random_id()
            scheduler.add_job(
                del_message,
                'interval',
                args=[message, scheduler, job_id],
                seconds=7,
                id=job_id
            )
            return
    form = await session.get_form_by_id(forms[0])
    forms.pop(0)
    user = await session.get_user(form.user_id)
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
    if form.photos:
        builder: MediaGroupBuilder = MediaGroupBuilder()
        for photo in form.photos:
            builder.add_photo(media=photo)
        await clb.message.answer_media_group(media=builder.build())
    await clb.message.answer(
        text=text,
        reply_markup=get_search_keyboard(translator, form_user_id=form.user_id)
    )
    await session.add_watch(clb.from_user.id, form.id)


@search_router.callback_query(F.data.startswith('contact'))
async def send_contact_data(clb: CallbackQuery, state: FSMContext, translator: Translator, session: DataInteraction):
    form_user_id = int(clb.data.split('_')[1])
    if not await session.add_request(sender=clb.from_user.id, receiver=form_user_id):
        await clb.answer(text=translator['add_request_error'])
        return
    await clb.answer(text=translator['add_request_success'])
    await clb.bot.send_message(
        chat_id=form_user_id,
        text=translator['add_request_message']
    )


@search_router.callback_query(F.data == 'help_info')
async def send_help_info(clb: CallbackQuery, translator: Translator, session: DataInteraction):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=translator['close_info_button'], callback_data='close_info')]]
    )
    form = await session.get_form(clb.from_user.id)
    text = translator['women_info'] if form.male == translator['women_button'] else translator['men_info']
    await clb.message.answer(text=text, reply_markup=keyboard)


@search_router.callback_query(F.data == 'close_info')
async def close_info(clb: CallbackQuery):
    await clb.message.delete()


@search_router.callback_query(F.data.startswith('complain'))
async def send_complain(clb: CallbackQuery, state: FSMContext, translator: Translator, session: DataInteraction):
    form_user_id = int(clb.data.split('_')[1])
    await state.set_data({'form_user_id': form_user_id})
    await state.set_state(searchSG.get_complain)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=translator['back'], callback_data='back_search')]]
    )
    await clb.message.answer(translator['get_complain'], reply_markup=keyboard)


@search_router.message(StateFilter(searchSG.get_complain))
async def get_complain(msg: Message, state: FSMContext, translator: Translator, session: DataInteraction, scheduler: AsyncIOScheduler):
    datas = await state.get_data()
    form_user_id = datas['form_user_id']
    await session.add_complain(msg.from_user.id, form_user_id, msg.text if msg.text else msg.caption)
    message = await msg.answer(translator['success_complain_add'])
    job_id = get_random_id()
    scheduler.add_job(
        del_message,
        'interval',
        args=[message, scheduler, job_id],
        seconds=7,
        id=job_id
    )
    await state.set_state(searchSG.search_menu)
    await msg.delete()


@search_router.callback_query(F.data == 'back_search', StateFilter(searchSG.get_complain))
async def back_search(clb: CallbackQuery, state: FSMContext, translator: Translator, session: DataInteraction):
    await state.set_state(searchSG.search_menu)
    await clb.message.delete()


@search_router.callback_query(F.data.startswith("get_contact"))
async def send_contact(clb: CallbackQuery, session: DataInteraction, translator, scheduler: AsyncIOScheduler):
    user_id = int(clb.data.split('_')[-1])
    user = await session.get_user(clb.from_user.id)
    form = await session.get_form(clb.from_user.id)
    price = 0
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
    sender = await session.get_user(user_id)
    await clb.message.answer(translator['success_my_request'].format(username=sender.username))
    await clb.bot.send_message(
        chat_id=sender.user_id,
        text=translator['success_alien_request'].format(form=text, username=clb.from_user.username)
    )
    await session.update_tokens(clb.from_user.id, -price)


