from aiogram.types import CallbackQuery, User, Message, ContentType
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram.utils.media_group import MediaGroupBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from keyboard.keyboards import get_check_photo_keyboard
from utils.translator.translator import Translator
from utils.text_utils import get_age_text
from utils.build_ids import get_random_id
from utils.schedulers import del_message
from database.action_data_class import DataInteraction
from config_data.config import load_config, Config
from states.state_groups import profileSG, formSG


config: Config = load_config()


async def start_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(event_from_user.id)
    form = await session.get_form(event_from_user.id)
    return {
        'text': translator['profile'].format(
            username='@' + user.username if user.username else '-',
            balance=user.balance,
            tokens=translator['tokens_widget'].format(tokens=user.tokens) if form.male == translator['men_button'] else '',
            vip=translator['vip_enable_widget'].format(vip=user.vip_end.strftime('%d-%m-%Y')) if (
                    user.vip and user.vip_end
            ) else translator['vip_disable_widget'] if not user.vip else translator['vip_enable_women'],
            form_status=translator['form_enable_widget'] if form.active else translator['form_disable_widget']
        ),
        'form_toggle': translator['disable_button'] if form.active else translator['enable_button'],
        'my_form': translator['my_form_button'],
        'refs': translator['refs_button'],
        'my_balance': translator['my_balance_button'],
        'language': translator['language_button']
    }


async def ref_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(event_from_user.id)
    return {
        'text': translator['ref'].format(user_id=user.user_id, refs=user.refs),
        'share': translator['share_button'],
        'user_id': event_from_user.id,
        'ref_static': translator['ref_static_button'],
        'back': translator['back']
    }


async def ref_static_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    transactions = await session.get_transactions(event_from_user.id)
    user = await session.get_user(event_from_user.id)
    print([
            transaction.sum if transaction.description == 'Вывод средств с баланса' else
            0 for transaction in transactions
        ])
    money = sum(
        [
            transaction.sum if transaction.description == 'Вывод средств с баланса' else
            0 for transaction in transactions
        ]
    )
    return {
        'text': translator['ref_static'].format(
            refs=user.refs,
            income=user.income,
            balance=user.balance,
            money=money
        ),
        'back': translator['back']
    }


async def toggle_form(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    form = await session.get_form(clb.from_user.id)
    if form.active:
        await session.set_form_active(clb.from_user.id, False)
    else:
        await session.set_form_active(clb.from_user.id, True)
    await dialog_manager.switch_to(profileSG.start)


async def form_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    form = await session.get_form(event_from_user.id)
    user = await session.get_user(event_from_user.id)
    media = None
    if form.photos:
        photo = MediaId(file_id=form.photos[0])
        media = MediaAttachment(file_id=photo, type=ContentType.PHOTO)
    return {
        'text_1': translator['see_form'],
        'text_2': translator['form'].format(
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
        ),
        'media': media,
        'name': translator['change_name_button'],
        'age': translator['change_age_button'],
        'male': translator['change_male_button'],
        'city': translator['change_city_button'],
        'profession': translator['change_profession_button'],
        'education': translator['change_education_button'],
        'income': translator['change_income_button'],
        'description': translator['change_plans_button'],
        'religion': translator['change_religion_button'],
        'second_wife': translator['change_second_wife_button'] if form.male == translator['women_button'] and form.religion == translator['add_religion_islam_button'] else False,
        'family': translator['change_family_button'],
        'children_count': translator['change_children_count_button'],
        'children': translator['change_children_button'],
        'leave': translator['change_leave_button'],
        'photos': translator['change_photos_button'],
        'start_form': translator['start_form_button'],
        'back': translator['back']
    }


async def get_name_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_name'],
        'back': translator['back']
    }


async def get_name(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if len(text) > 50:
        translator: Translator = dialog_manager.middleware_data.get('translator')
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        message = await msg.answer(text=translator['add_name_error'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_form(msg.from_user.id, name=text)
    await msg.delete()
    await dialog_manager.switch_to(profileSG.form_menu, show_mode=ShowMode.EDIT)


async def get_age_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_age'],
        'back': translator['back']
    }


async def get_age(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    try:
        age = int(text)
    except Exception as err:
        translator: Translator = dialog_manager.middleware_data.get('translator')
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        message = await msg.answer(text=translator['add_age_error'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        return
    if age <= 18 or age >= 99:
        translator: Translator = dialog_manager.middleware_data.get('translator')
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        message = await msg.answer(text=translator['add_age_error'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_form(msg.from_user.id, age=age)
    await msg.delete()
    await dialog_manager.switch_to(profileSG.form_menu, show_mode=ShowMode.EDIT)


async def get_male_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['change_male'],
        'start_form': translator['start_form_button'],
        'back': translator['back']
    }


async def choose_male(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    await session.update_vip(clb.from_user.id, False)
    job = scheduler.get_job(job_id=str(clb.from_user.id))
    if job:
        job.remove()
    await dialog_manager.done()
    await clb.message.delete()
    await session.del_requests(clb.from_user.id)
    await dialog_manager.start(formSG.get_name)


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
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_form(msg.from_user.id, city=text)
    await msg.delete()
    await dialog_manager.switch_to(profileSG.form_menu, show_mode=ShowMode.EDIT)


async def get_profession_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_profession'],
        'back': translator['back']
    }


async def get_profession(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if len(text) > 100:
        translator: Translator = dialog_manager.middleware_data.get('translator')
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        message = await msg.answer(text=translator['add_profession_error'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_form(msg.from_user.id, profession=text[0].upper() + text[1::])
    await msg.delete()
    await dialog_manager.switch_to(profileSG.form_menu, show_mode=ShowMode.EDIT)


async def get_education_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_education'],
        'leaning': translator['add_education_leaning_button'],
        'eleven': translator['add_education_eleven_button'],
        'average': translator['add_education_average_button'],
        'higher': translator['add_education_higher_button'],
        'back': translator['back']
    }


async def choose_education(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('leaning'):
        education = clb.message.reply_markup.inline_keyboard[0][0].text
    elif clb.data.startswith('eleven'):
        education = clb.message.reply_markup.inline_keyboard[1][0].text
    elif clb.data.startswith('average'):
        education = clb.message.reply_markup.inline_keyboard[2][0].text
    else:
        education = clb.message.reply_markup.inline_keyboard[3][0].text
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_form(clb.from_user.id, education=education)
    await dialog_manager.switch_to(profileSG.form_menu, show_mode=ShowMode.EDIT)


async def get_income_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_income'],
        'no': translator['add_income_no_button'],
        'low': translator['add_income_low_button'],
        'average': translator['add_income_average_button'],
        'high': translator['add_income_high_button'],
        'back': translator['back']
    }


async def choose_income(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('no'):
        income = clb.message.reply_markup.inline_keyboard[0][0].text
    elif clb.data.startswith('low'):
        income = clb.message.reply_markup.inline_keyboard[1][0].text
    elif clb.data.startswith('average'):
        income = clb.message.reply_markup.inline_keyboard[2][0].text
    else:
        income = clb.message.reply_markup.inline_keyboard[3][0].text
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_form(clb.from_user.id, income=income)
    await dialog_manager.switch_to(profileSG.form_menu, show_mode=ShowMode.EDIT)


async def get_plans_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_plans'],
        'back': translator['back']
    }


async def get_plans(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if len(text) > 500:
        translator: Translator = dialog_manager.middleware_data.get('translator')
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        message = await msg.answer(text=translator['add_plans_error'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_form(msg.from_user.id, description=text)
    await msg.delete()
    await dialog_manager.switch_to(profileSG.form_menu, show_mode=ShowMode.EDIT)


async def get_religion_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_religion'],
        'christian': translator['add_religion_christian_button'],
        'islam': translator['add_religion_islam_button'],
        'another': translator['add_religion_another_button'],
        'back': translator['back']
    }


async def choose_religion(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    if clb.data.startswith('christian'):
        religion = clb.message.reply_markup.inline_keyboard[0][0].text
    elif clb.data.startswith('islam'):
        religion = clb.message.reply_markup.inline_keyboard[1][0].text
    else:
        religion = clb.message.reply_markup.inline_keyboard[2][0].text
    await session.update_form(clb.from_user.id, religion=religion)
    await dialog_manager.switch_to(profileSG.form_menu, show_mode=ShowMode.EDIT)


async def get_second_wife_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_second_wife'],
        'yes': translator['add_second_wife_yes_button'],
        'no': translator['add_second_wife_no_button'],
        'back': translator['back']
    }


async def choose_second_wife(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('yes'):
        second_wife = 1
    else:
        second_wife = 0
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_form(clb.from_user.id, second_wife=second_wife)
    await dialog_manager.switch_to(profileSG.form_menu, show_mode=ShowMode.EDIT)


async def get_family_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    form = await session.get_form(event_from_user.id)
    return {
        'text': translator['add_family'],
        'family': translator['family_button'] if form.male == translator['men_button'] and form.religion == translator['add_religion_islam_button'] else False,
        'no_family': translator['no_family_button_men'] if form.male == translator['men_button'] else translator['no_family_button_women'],
        'divorce_family': translator['divorce_family_button_men'] if form.male == translator['men_button'] else translator['divorce_family_button_women'],
        'widow_family': translator['widow_family_button_men'] if form.male == translator['men_button'] else translator['widow_family_button_women'],
        'back': translator['back']
    }


async def choose_family(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('no'):
        family = clb.message.reply_markup.inline_keyboard[1][0].text
    elif clb.data.startswith('divorce'):
        family = clb.message.reply_markup.inline_keyboard[2][0].text
    elif clb.data.startswith('family'):
        family = clb.message.reply_markup.inline_keyboard[0][0].text
    else:
        family = clb.message.reply_markup.inline_keyboard[3][0].text
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_form(clb.from_user.id, family=family)
    await dialog_manager.switch_to(profileSG.form_menu, show_mode=ShowMode.EDIT)


async def get_children_count_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_children_count'],
        'no_children': translator['add_children_count_no_button'],
        'back': translator['back']
    }


async def get_children_count(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    try:
        count = int(text)
    except Exception as err:
        message = await msg.answer(translator['add_children_count_error'])
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        return
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_form(msg.from_user.id, children_count=str(count))
    await dialog_manager.switch_to(profileSG.form_menu, show_mode=ShowMode.EDIT)


async def choose_children_count(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_form(clb.from_user.id, children_count=clb.message.reply_markup.inline_keyboard[0][0].text)
    await dialog_manager.switch_to(profileSG.form_menu, show_mode=ShowMode.EDIT)


async def get_children_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_children'],
        'yes': translator['add_children_yes_button'],
        'no': translator['add_children_no_button'],
        'maybe': translator['add_children_maybe_button'],
        'not_matter': translator['add_children_not_matter_button'],
        'back': translator['back']
    }


async def choose_children(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('yes'):
        # можно делать через widget
        children = clb.message.reply_markup.inline_keyboard[0][0].text
    elif clb.data.startswith('no_'):
        children = clb.message.reply_markup.inline_keyboard[1][0].text
    elif clb.data.startswith('maybe'):
        children = clb.message.reply_markup.inline_keyboard[2][0].text
    else:
        children = clb.message.reply_markup.inline_keyboard[3][0].text
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_form(clb.from_user.id, children=children)
    await dialog_manager.switch_to(profileSG.form_menu, show_mode=ShowMode.EDIT)


async def get_leave_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_leave'],
        'back': translator['back']
    }


async def choose_leave(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('yes'):
        leave = clb.message.reply_markup.inline_keyboard[0][0].text
    else:
        leave = clb.message.reply_markup.inline_keyboard[1][0].text
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    await session.update_form(clb.from_user.id, leave=leave)
    await dialog_manager.switch_to(profileSG.form_menu, show_mode=ShowMode.EDIT)


async def get_photo_1_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_photo_1'],
        'back': translator['back']
    }


async def get_photo_1(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    print(msg.photo[-1].file_id)
    dialog_manager.dialog_data['photos'] = [msg.photo[-1].file_id]
    print(dialog_manager.dialog_data.get('photos'))
    await msg.delete()
    await dialog_manager.switch_to(profileSG.get_photo_2, show_mode=ShowMode.EDIT)


async def get_photo_2_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_photo_2'],
        'skip': translator['add_photo_skip'],
        'back': translator['back']
    }


async def get_photo_2(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    photos: list = dialog_manager.dialog_data.get('photos')
    photos.append(msg.photo[-1].file_id)
    dialog_manager.dialog_data['photos'] = photos
    await msg.delete()
    await dialog_manager.switch_to(profileSG.get_photo_3, show_mode=ShowMode.EDIT)


async def get_photo_3_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_photo_3'],
        'skip': translator['add_photo_skip'],
        'back': translator['back']
    }


async def get_photo_3(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    photos: list = dialog_manager.dialog_data.get('photos')
    photos.append(msg.photo[-1].file_id)

    admins = [i.user_id for i in await session.get_admins()]
    admins.extend(config.bot.admin_ids)

    builder: MediaGroupBuilder = MediaGroupBuilder(
        caption='Заявка на проверку фоток юзера',
    )
    if photos:
        for photo in photos:
            builder.add_photo(photo)

        for admin in [5474650891]:
            message = await msg.bot.send_media_group(
                chat_id=admin,
                media=builder.build(),
            )
            form = await session.get_form(msg.from_user.id)
            user = await session.get_user(msg.from_user.id)
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
            ) + f'\n\nЗаявка на проверку фоток от пользователя @{user.username}'
            await msg.bot.send_message(
                chat_id=admin,
                text=text,
                reply_markup=get_check_photo_keyboard(msg.from_user.id)
            )
            await session.add_application(
                user_id=msg.from_user.id,
                photos=photos,
                message_ids=[msg.message_id for msg in message]
            )
    if photos:
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        message = await msg.answer(translator['check_photos'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
    await msg.delete()
    await dialog_manager.switch_to(profileSG.form_menu, show_mode=ShowMode.EDIT)


async def skip_get_photos(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    photos: list = dialog_manager.dialog_data.get('photos')

    admins = [i.user_id for i in await session.get_admins()]
    admins.extend(config.bot.admin_ids)

    builder: MediaGroupBuilder = MediaGroupBuilder(
        caption='Заявка на проверку фоток юзера',
    )
    if photos:
        for photo in photos:
            builder.add_photo(photo)

        for admin in [5474650891]:
            message = await clb.bot.send_media_group(
                chat_id=admin,
                media=builder.build(),
            )
            form = await session.get_form(clb.from_user.id)
            user = await session.get_user(clb.from_user.id)
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
            ) + f'\n\nЗаявка на проверку фоток от пользователя @{user.username}'
            await clb.bot.send_message(
                chat_id=admin,
                text=text,
                reply_markup=get_check_photo_keyboard(clb.from_user.id)
            )
            await session.add_application(
                user_id=clb.from_user.id,
                photos=photos,
                message_ids=[msg.message_id for msg in message]
            )
    if photos:
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        message = await clb.message.answer(translator['check_photos'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
    await dialog_manager.switch_to(profileSG.form_menu)

