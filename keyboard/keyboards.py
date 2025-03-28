from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from utils.translator.translator import Translator


def get_start_keyboard(translator: Translator, admin: bool):
    keyboard = [
            [
                KeyboardButton(text=translator['profile_button']),
                KeyboardButton(text=translator['search_partner_button'])
            ],
            [
                KeyboardButton(text=translator['requests_button']),
                KeyboardButton(text=translator['balance_button'])
            ],
            [
                KeyboardButton(text=translator['info_button']),
                KeyboardButton(text=translator['help_button'])
            ],
        ]
    if admin:
        keyboard.append([KeyboardButton(text='Админ панель')])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def get_search_keyboard(translator: Translator, form_user_id: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=translator['next_form_button'], callback_data='next'),
                InlineKeyboardButton(text=translator['complain_form_button'], callback_data=f'complain_{form_user_id}')
            ],
            [
                InlineKeyboardButton(text=translator['contact_form_button'], callback_data=f'contact_{form_user_id}'),
                InlineKeyboardButton(text=translator['form_info_button'], callback_data=f'help_info')
            ]
        ]
    )
    return keyboard


def get_check_photo_keyboard(user_id: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Подтвердить', callback_data=f'photos|{user_id}')
            ],
            [
                InlineKeyboardButton(text='Отклонить', callback_data=f'revoke|{user_id}')
            ],
            [
                InlineKeyboardButton(text='Заблокировать', callback_data=f'block_user|{user_id}')
            ]
        ]
    )
    return keyboard


def get_start_women_verification(translator: Translator):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=translator['women_verification_button'], callback_data='women_verification')],
            [InlineKeyboardButton(text=translator['back'], callback_data='close_vip_window')]
        ]
    )
    return keyboard


def derive_user_balance_keyboard(user_id: int, amount: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Снять у пользователя средства', callback_data=f'derive_{user_id}_{amount}')],
            [InlineKeyboardButton(text='Удалить заявку', callback_data='del_derive_application')]
        ]
    )
    return keyboard


def get_check_note_keyboard(user_id: int):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Одобрить заявку', callback_data=f'verification_{user_id}')],
            [InlineKeyboardButton(text='Отклонить заявку', callback_data='cancel_verification')]
        ]
    )
    return keyboard

