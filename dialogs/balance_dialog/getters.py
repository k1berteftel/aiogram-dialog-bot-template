import datetime

import uuid
from aiogram import Bot
from aiogram.types import CallbackQuery, User, Message, ContentType
from aiogram.fsm.context import FSMContext
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import Button, Select
from aiogram_dialog.widgets.input import ManagedTextInput
from dateutil.relativedelta import relativedelta
from yookassa import Configuration, Payment
from yookassa.payment import PaymentResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from keyboard.keyboards import derive_user_balance_keyboard
from config_data.config import Config, load_config
from utils.translator.translator import Translator
from utils.schedulers import check_vip, check_payment, del_message
from utils.tables import get_table
from utils.build_ids import get_random_id
from database.action_data_class import DataInteraction
from config_data.config import load_config, Config
from states.state_groups import balanceSG, women_verificationSG


config: Config = load_config()

Configuration.account_id = 1011354
Configuration.secret_key = config.payment.api_key


async def start_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(event_from_user.id)
    form = await session.get_form(event_from_user.id)
    translator: Translator = dialog_manager.middleware_data.get('translator')
    if form.male == translator['men_button']:
        text = translator['balance'].format(
            balance=user.balance,
            tokens=user.tokens,
            vip=(translator['vip_enable_widget'].format(vip=user.vip_end.strftime('%d-%m-%Y')) if (user.vip and user.vip_end
            ) else translator['vip_disable_widget'] if not user.vip else translator['vip_enable_women']),
        )
    else:
        if user.vip:
            text = translator['women_vip']
        else:
            text = translator['women_vip_proposal']
    return {
        'text': text,
        'payment': translator['payment_button'],
        'vip': translator['vip_button'],
        'get_vip': translator['women_verification_button'],
        'balance': translator['balance_menu_button'],
        'history': translator['history_button'],
        'back': translator['back'],
        'men': form.male == translator['men_button'],
        'women': (form.male == translator['women_button']) and not user.vip
    }


async def get_vip_switcher(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    state: FSMContext = dialog_manager.middleware_data.get('state')
    translator: Translator = dialog_manager.middleware_data.get('translator')
    await dialog_manager.done()
    await clb.message.delete()
    await state.set_state(women_verificationSG.get_video_note)
    await clb.message.answer(translator['women_verification_note'])


async def balance_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    user = await session.get_user(event_from_user.id)
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['balance_menu'].format(
            balance=user.balance
        ),
        'derive': translator['derive_button'],
        'history': translator['history_button'],
        'back': translator['back']
    }


async def get_derive_amount(msg: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    await msg.delete()
    try:
        amount = int(text)
    except Exception:
        message = await msg.answer(translator['derive_integer_error'])
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
    user = await session.get_user(msg.from_user.id)
    if user.balance < amount:
        message = await msg.answer(translator['derive_balance_error'])
        job_id = get_random_id()
        scheduler.add_job(
            del_message,
            'interval',
            args=[message, scheduler, job_id],
            seconds=7,
            id=job_id
        )
        return
    text = (f'<b>Заявка на вывод средств от пользователя {msg.from_user.id}</b>\n'
            f'Данные по заявке:\n - Сумма для вывода: {amount}\n - Юзернейм пользователя: {msg.from_user.username}')
    for admin_id in config.bot.admin_ids:
        await msg.bot.send_message(
            chat_id=admin_id,
            text=text,
            reply_markup=derive_user_balance_keyboard(msg.from_user.id, amount)
        )
    message = await msg.answer(translator['success_derive_application'])
    job_id = get_random_id()
    scheduler.add_job(
        del_message,
        'interval',
        args=[message, scheduler, job_id],
        seconds=7,
        id=job_id
    )
    await dialog_manager.switch_to(balanceSG.balance_menu)


async def balance_derive_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['balance_derive'],
        'back': translator['back']
    }


async def choose_rate(clb: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rate = await session.get_rate(int(item_id))
    dialog_manager.dialog_data['tokens'] = rate.amount
    dialog_manager.dialog_data['price'] = rate.price
    dialog_manager.dialog_data['type'] = 'rate'
    await dialog_manager.switch_to(balanceSG.tokens_confirm)


async def payment_menu_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    rates = await session.get_rates()
    buttons = []
    for rate in rates:
        buttons.append((f'⚡️{rate.amount} - {rate.price} {translator["rub"]}', rate.id))
    return {
        'text': translator['choose_tokens'],
        'items': buttons,
        'back': translator['back']
    }


async def tokens_confirm_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    tokens = dialog_manager.dialog_data.get('tokens')
    price = dialog_manager.dialog_data.get('price')
    return {
        'text': translator['tokens_confirm'].format(tokens=tokens, price=price),
        'yes': translator['confirm_tokens_button'],
        'back': translator['back']
    }


async def choose_payment_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['choose_payment'],
        'card_pay': translator['card_pay_button'],
        'crypto_pay': translator['crypto_pay_button'],
        'back': translator['back']
    }


async def card_pay_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    amount = dialog_manager.dialog_data.get('price')
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    bot: Bot = dialog_manager.middleware_data.get('bot')
    print(str(amount)+ '.00')
    type = dialog_manager.dialog_data.get('type')
    payment = await Payment.create({
        "amount": {
            "value": str(amount) + '.00',
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": "https://t.me/Origandtocha_bot"
        },
        "receipt": {
            "customer": {
                "email": "ibankrot05@gmail.com"
            },
            'items': [
                {
                    "description": "Покупка токенов в боте" if type == 'rate' else "Приобретение vip в боте",
                    "amount": {
                        "value": str(amount) + '.00',
                        "currency": "RUB"
                    },
                    'measure': 'another',
                    'vat_code': 1,
                    'quantity': 1,
                    'payment_subject': 'payment',
                    'payment_mode': 'full_payment'
                }
            ]
        },
        "capture": True,
        "description": "Покупка токенов в боте" if type == 'rate' else "Приобретение vip в боте",
    }, uuid.uuid4())
    url = payment.confirmation.confirmation_url
    days = dialog_manager.dialog_data.get('days')
    scheduler.add_job(
        check_payment,
        'interval',
        args=[payment.id, event_from_user.id, bot, scheduler, session, translator],
        id=f'payment_{event_from_user.id}',
        kwargs={'tokens': dialog_manager.dialog_data.get('tokens'), 'amount': amount,
                'type': type, 'date': relativedelta(days=days) if days else None},
        seconds=5
    )
    return {
        'text': translator['get_pay'],
        'url': url,
        'url_text': translator['url_button'],
        'back': translator['back']
    }


async def back_choose_payment(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    scheduler: AsyncIOScheduler = dialog_manager.middleware_data.get('scheduler')
    job = scheduler.get_job(job_id=f'payment_{clb.from_user.id}')
    if job:
        job.remove()
    await dialog_manager.switch_to(balanceSG.choose_payment_menu)


async def crypto_pay_getter(dialog_manager: DialogManager, **kwargs):
    translator: Translator = dialog_manager.middleware_data.get('translator')
    # логика создания ссылки на оплату по крипте
    return {
        'text': translator['get_pay'],
        'url_text': translator['url_button'],
        'check': translator['check_pay_button'],
        'back': translator['back']
    }


async def toggle_vip(clb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    category = clb.data.split('_')[0]
    if category == 'one':
        price = 299
        days = 1
    elif category == 'three':
        price = 499
        days = 3
    else:
        price = 999
        days = 7
    dialog_manager.dialog_data['price'] = price
    dialog_manager.dialog_data['days'] = days
    dialog_manager.dialog_data['type'] = 'vip'
    await dialog_manager.switch_to(balanceSG.choose_payment_menu)


async def vip_choose_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['choose_vip'],
        'one_day': translator['one_day_button'],
        'three_days': translator['three_day_button'],
        'one_week': translator['one_week_button'],
        'back': translator['back']
    }


async def vip_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    translator: Translator = dialog_manager.middleware_data.get('translator')
    return {
        'text': translator['vip'],
        'vip_switcher': translator['on_vip_button'],
        'back': translator['back']
    }


async def history_menu_getter(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    session: DataInteraction = dialog_manager.middleware_data.get('session')
    transaction = await session.get_transactions(event_from_user.id)
    tables = []
    for row in transaction:
        tables.append(
            [
                row.create,
                row.sum,
                row.description
            ]
        )
    tables.insert(0, ['Дата', 'сумма', 'описание'])
    table = get_table(tables)
    translator: Translator = dialog_manager.middleware_data.get('translator')
    media = MediaAttachment(type=ContentType.DOCUMENT, path=table)
    return {
        'media': media,
        'text': translator['history'],
        'back': translator['back']
    }
