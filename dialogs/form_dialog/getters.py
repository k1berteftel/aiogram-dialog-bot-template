from aiogram.types import CallbackQuery, User, Message, InlineKeyboardMarkup
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram.utils.media_group import MediaGroupBuilder
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config_data.config import Config, load_config
from keyboard.keyboards import get_start_keyboard, get_check_photo_keyboard, get_start_women_verification
from utils.translator.translator import Translator
from utils.schedulers import del_message
from utils.text_utils import get_age_text
from utils.build_ids import get_random_id
from database.action_data_class import DataInteraction
from config_data.config import load_config, Config
from states.state_groups import formSG


config: Config = load_config()


async def get_name_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_name']
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
        await msg.delete()
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
        return
    dialog_manager.dialog_data['name'] = text
    await msg.delete()
    await dialog_manager.switch_to(formSG.get_age, show_mode=ShowMode.DELETE_AND_SEND)


async def get_age_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_age'],
        'back': translator['back']
    }


async def get_age(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    try:
        age = int(text)
    except Exception as err:
        translator: Translator = dialog_manager.middleware_data.get('translator')
        message = await msg.answer(text=translator['add_age_error'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        await msg.delete()
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception as err:
            print(err)
        return
    if age <= 17 or age >= 99:
        translator: Translator = dialog_manager.middleware_data.get('translator')
        message = await msg.answer(text=translator['add_age_error'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        await msg.delete()
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
        return
    dialog_manager.dialog_data['age'] = age
    await msg.delete()
    await dialog_manager.switch_to(formSG.get_male, show_mode=ShowMode.DELETE_AND_SEND)


async def get_male_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_male'],
        'men': translator['men_button'],
        'women': translator['women_button'],
        'back': translator['back']
    }


async def choose_male(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('men'):
        dialog_manager.dialog_data['male'] = clb.message.reply_markup.inline_keyboard[0][0].text
    else:
        dialog_manager.dialog_data['male'] = clb.message.reply_markup.inline_keyboard[1][0].text
    await dialog_manager.switch_to(formSG.get_city, show_mode=ShowMode.DELETE_AND_SEND)


async def get_city_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_city'],
        'back': translator['back']
    }


async def get_city(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if len(text) > 30:
        await msg.delete()
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        translator: Translator = dialog_manager.middleware_data.get('translator')
        message = await msg.answer(text=translator['add_city_error'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
        return
    dialog_manager.dialog_data['city'] = text[0].upper() + text[1::]
    await msg.delete()
    await dialog_manager.switch_to(formSG.get_profession, show_mode=ShowMode.DELETE_AND_SEND)


async def get_profession_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_profession'],
        'back': translator['back']
    }


async def get_profession(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if len(text) > 100:
        await msg.delete()
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
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
        return
    dialog_manager.dialog_data['profession'] = text[0].upper() + text[1::]
    await msg.delete()
    await dialog_manager.switch_to(formSG.get_education, show_mode=ShowMode.DELETE_AND_SEND)


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
        dialog_manager.dialog_data['education'] = clb.message.reply_markup.inline_keyboard[0][0].text
    elif clb.data.startswith('eleven'):
        dialog_manager.dialog_data['education'] = clb.message.reply_markup.inline_keyboard[1][0].text
    elif clb.data.startswith('average'):
        dialog_manager.dialog_data['education'] = clb.message.reply_markup.inline_keyboard[2][0].text
    else:
        dialog_manager.dialog_data['education'] = clb.message.reply_markup.inline_keyboard[3][0].text
    await dialog_manager.switch_to(formSG.get_income, show_mode=ShowMode.DELETE_AND_SEND)


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
        dialog_manager.dialog_data['income'] = clb.message.reply_markup.inline_keyboard[0][0].text
    elif clb.data.startswith('low'):
        dialog_manager.dialog_data['income'] = clb.message.reply_markup.inline_keyboard[1][0].text
    elif clb.data.startswith('average'):
        dialog_manager.dialog_data['income'] = clb.message.reply_markup.inline_keyboard[2][0].text
    else:
        dialog_manager.dialog_data['income'] = clb.message.reply_markup.inline_keyboard[3][0].text
    await dialog_manager.switch_to(formSG.get_description, show_mode=ShowMode.DELETE_AND_SEND)


async def get_description_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_plans'],
        'back': translator['back']
    }


async def get_description(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    if len(text) > 1000:
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
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
        await msg.delete()
        return
    dialog_manager.dialog_data['description'] = text
    await msg.delete()
    await dialog_manager.switch_to(formSG.get_religion, show_mode=ShowMode.DELETE_AND_SEND)


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
    if clb.data.startswith('christian'):
        dialog_manager.dialog_data['religion'] = clb.message.reply_markup.inline_keyboard[1][0].text
    elif clb.data.startswith('islam'):
        dialog_manager.dialog_data['religion'] = clb.message.reply_markup.inline_keyboard[0][0].text
        if dialog_manager.dialog_data.get('male') == translator['women_button']:
            await dialog_manager.switch_to(formSG.get_second_wife, show_mode=ShowMode.DELETE_AND_SEND)
            return
    else:
        dialog_manager.dialog_data['religion'] = clb.message.reply_markup.inline_keyboard[2][0].text
    await dialog_manager.switch_to(formSG.get_family, show_mode=ShowMode.DELETE_AND_SEND)


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
        dialog_manager.dialog_data['second_wife'] = 1
    else:
        dialog_manager.dialog_data['second_wife'] = 0
    await dialog_manager.switch_to(formSG.get_family, show_mode=ShowMode.DELETE_AND_SEND)


async def get_family_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_family'],
        'family': translator['family_button'] if dialog_manager.dialog_data.get('male') == translator['men_button'] and dialog_manager.dialog_data.get('religion') == translator['add_religion_islam_button'] else False,
        'no_family': translator['no_family_button_men'] if dialog_manager.dialog_data.get('male') == translator['men_button'] else translator['no_family_button_women'],
        'divorce_family': translator['divorce_family_button_men'] if dialog_manager.dialog_data.get('male') == translator['men_button'] else translator['divorce_family_button_women'],
        'widow_family': translator['widow_family_button_men'] if dialog_manager.dialog_data.get('male') == translator['men_button'] else translator['widow_family_button_women'],
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
    await dialog_manager.switch_to(formSG.get_children_count, show_mode=ShowMode.DELETE_AND_SEND)


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
        scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
        message = await msg.answer(translator['add_children_count_error'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        try:
            await msg.bot.delete_message(chat_id=msg.from_user.id, message_id=msg.message_id - 1)
        except Exception:
            ...
        await msg.delete()
        return
    dialog_manager.dialog_data['children_count'] = count
    await dialog_manager.switch_to(formSG.get_children, show_mode=ShowMode.DELETE_AND_SEND)


async def choose_children_count(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['children_count'] = clb.message.reply_markup.inline_keyboard[0][0].text
    await dialog_manager.switch_to(formSG.get_children, show_mode=ShowMode.DELETE_AND_SEND)


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
        dialog_manager.dialog_data['children'] = clb.message.reply_markup.inline_keyboard[0][0].text
    elif clb.data.startswith('no_'):
        dialog_manager.dialog_data['children'] = clb.message.reply_markup.inline_keyboard[1][0].text
    elif clb.data.startswith('maybe'):
        dialog_manager.dialog_data['children'] = clb.message.reply_markup.inline_keyboard[2][0].text
    else:
        dialog_manager.dialog_data['children'] = clb.message.reply_markup.inline_keyboard[3][0].text
    await dialog_manager.switch_to(formSG.get_leave, show_mode=ShowMode.DELETE_AND_SEND)


async def get_leave_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_leave'],
        'yes': translator['add_leave_yes_button'],
        'no': translator['add_leave_no_button'],
        'back': translator['back']
    }


async def choose_leave(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    if clb.data.startswith('yes'):
        dialog_manager.dialog_data['leave'] = clb.message.reply_markup.inline_keyboard[0][0].text
    else:
        dialog_manager.dialog_data['leave'] = clb.message.reply_markup.inline_keyboard[1][0].text
    await dialog_manager.switch_to(formSG.get_photo_1, show_mode=ShowMode.DELETE_AND_SEND)


async def get_photo_1_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['add_photo_1'],
        'skip': translator['add_photo_skip'],
        'back': translator['back']
    }


async def get_photo_1(msg: Message, widget: MessageInput, dialog_manager: DialogManager):
    print(msg.photo[-1].file_id)
    dialog_manager.dialog_data['photos'] = [msg.photo[-1].file_id]
    print(dialog_manager.dialog_data.get('photos'))
    await msg.delete()
    await dialog_manager.switch_to(formSG.get_photo_2, show_mode=ShowMode.DELETE_AND_SEND)


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
    await dialog_manager.switch_to(formSG.get_photo_3, show_mode=ShowMode.DELETE_AND_SEND)


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
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    photos: list = dialog_manager.dialog_data.get('photos')
    photos.append(msg.photo[-1].file_id)
    dialog_manager.dialog_data['photos'] = photos

    admins = [i.user_id for i in await session.get_admins()]
    admins.extend(config.bot.admin_ids)

    #  ___
    name = dialog_manager.dialog_data.get('name')
    age = dialog_manager.dialog_data.get('age')
    male = dialog_manager.dialog_data.get('male')
    city = dialog_manager.dialog_data.get('city')
    profession = dialog_manager.dialog_data.get('profession')
    education = dialog_manager.dialog_data.get('education')
    income = dialog_manager.dialog_data.get('income')
    description = dialog_manager.dialog_data.get('description')
    religion = dialog_manager.dialog_data.get('religion')
    second_wife = dialog_manager.dialog_data.get('second_wife')
    family = dialog_manager.dialog_data.get('family')
    children_count = dialog_manager.dialog_data.get('children_count')
    children = dialog_manager.dialog_data.get('children')
    leave = dialog_manager.dialog_data.get('leave')
    form = await session.get_form(msg.from_user.id)
    await session.add_form(
        user_id=msg.from_user.id,
        name=name,
        age=age,
        male=male,
        city=city,
        profession=profession,
        education=education,
        income=income,
        description=description,
        religion=religion,
        second_wife=second_wife,
        family=family,
        children_count=children_count,
        children=children,
        leave=leave
    )
    message = await msg.answer(translator['add_form_notification'])
    job_id = get_random_id()
    scheduler.add_job(
        del_message,
        'interval',
        args=[message, scheduler, job_id],
        seconds=7,
        id=job_id
    )
    #  ___

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
            text = ((translator['form'].format(
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
                vip='✅' if user.vip else '❌')) if form else "<b>Анкета отсутствует</b>"
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
    if (
            (form and (form.male == translator['men_button'] and male == translator['women_button'])) or
            (not form and male == translator['women_button'])
    ):
        await dialog_manager.done()
        await msg.delete()
        keyboard = get_start_women_verification(translator)
        await msg.answer(translator['women_vip_proposal'], reply_markup=keyboard)
        return
    admin = False
    if msg.from_user.id in admins:
        admin = True
    await msg.answer(
        text=translator['hello'],
        reply_markup=get_start_keyboard(translator, admin)
    )
    await dialog_manager.done()
    await msg.delete()


async def skip_get_photos(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    photos: list = dialog_manager.dialog_data.get('photos')

    #  ___
    name = dialog_manager.dialog_data.get('name')
    age = dialog_manager.dialog_data.get('age')
    male = dialog_manager.dialog_data.get('male')
    city = dialog_manager.dialog_data.get('city')
    profession = dialog_manager.dialog_data.get('profession')
    education = dialog_manager.dialog_data.get('education')
    income = dialog_manager.dialog_data.get('income')
    description = dialog_manager.dialog_data.get('description')
    religion = dialog_manager.dialog_data.get('religion')
    second_wife = dialog_manager.dialog_data.get('second_wife')
    family = dialog_manager.dialog_data.get('family')
    children_count = dialog_manager.dialog_data.get('children_count')
    children = dialog_manager.dialog_data.get('children')
    leave = dialog_manager.dialog_data.get('leave')
    form = await session.get_form(clb.from_user.id)
    await session.add_form(
        user_id=clb.from_user.id,
        name=name,
        age=age,
        male=male,
        city=city,
        profession=profession,
        education=education,
        income=income,
        description=description,
        religion=religion,
        second_wife=second_wife,
        family=family,
        children_count=children_count,
        children=children,
        leave=leave
    )
    message = await clb.message.answer(translator['add_form_notification'])
    job_id = get_random_id()
    scheduler.add_job(
        del_message,
        'interval',
        args=[message, scheduler, job_id],
        seconds=7,
        id=job_id
    )
    #  ___

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
            text = ((translator['form'].format(
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
                vip='✅' if user.vip else '❌')) if form else "<b>Анкета отсутствует</b>"
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
        message = await clb.message.answer(translator['check_photos'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
    #  ______
    if (
            (form and (form.male == translator['men_button'] and male == translator['women_button'])) or
            (not form and male == translator['women_button'])
    ):
        await dialog_manager.done()
        await clb.message.delete()
        keyboard = get_start_women_verification(translator)
        await clb.message.answer(translator['women_vip_proposal'], reply_markup=keyboard)
        return
    admin = False
    if clb.from_user.id in admins:
        admin = True
    await clb.message.answer(
        text=translator['hello'],
        reply_markup=get_start_keyboard(translator, admin)
    )
    await dialog_manager.done()
    await clb.message.delete()
