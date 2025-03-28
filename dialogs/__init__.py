from aiogram_dialog import Dialog

from dialogs.admin_dialog.dialog import admin_dialog
from dialogs.profile_dialog.dialog import profile_dialog
from dialogs.search_dialog.dialog import search_dialog
from dialogs.requests_dialog.dialog import requests_dialog
from dialogs.info_dialog.dialog import info_dialog
from dialogs.balance_dialog.dialog import balance_dialog
from dialogs.help_dialog.dialog import help_dialog
from dialogs.form_dialog.dialog import form_dialog
from dialogs.language_dialog.dialog import language_dialog
from dialogs.targeting_dialog.dialog import targeting_dialog
from dialogs.sub_dialog.dialog import sub_dialog


def get_dialogs() -> list[Dialog]:
    return [profile_dialog, form_dialog, search_dialog, requests_dialog, info_dialog,
            balance_dialog, help_dialog, admin_dialog, targeting_dialog,
            language_dialog, sub_dialog]
