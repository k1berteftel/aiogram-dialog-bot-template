from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Row, Button, Group, Select, Start, Url, Cancel
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.media import DynamicMedia

from dialogs.balance_dialog import getters

from states.state_groups import balanceSG


balance_dialog = Dialog(
    Window(
        Format('{text}'),
        Column(
            SwitchTo(Format('{payment}'), id='payment_menu_switcher', state=balanceSG.payment_menu, when='men'),
            SwitchTo(Format('{vip}'), id='vip_menu_switcher', state=balanceSG.vip_menu, when='men'),
            SwitchTo(Format('{balance}'), id='balance_menu_switcher', state=balanceSG.balance_menu),
            SwitchTo(Format('{history}'), id='history_menu_switcher', state=balanceSG.history_menu, when='men'),
            Button(Format('{get_vip}'), id='get_vip_switcher', on_click=getters.get_vip_switcher, when='women'),
            Cancel(Format('{back}'), id='close_dialog'),
        ),
        getter=getters.start_getter,
        state=balanceSG.start
    ),
    Window(
        Format('{text}'),
        Column(
            SwitchTo(Format('{derive}'), id='balance_derive_switcher', state=balanceSG.balance_derive),
            SwitchTo(Format('{history}'), id='history_menu_switcher', state=balanceSG.history_menu)
        ),
        SwitchTo(Format('{back}'), id='back', state=balanceSG.start),
        getter=getters.balance_menu_getter,
        state=balanceSG.balance_menu
    ),
    Window(
        Format('{text}'),
        TextInput(
            id='get_derive_amount',
            on_success=getters.get_derive_amount
        ),
        SwitchTo(Format('{back}'), id='back_balance_menu', state=balanceSG.balance_menu),
        getter=getters.balance_derive_getter,
        state=balanceSG.balance_derive
    ),
    Window(
        Format('{text}'),
        Group(
            Select(
                Format('{item[0]}'),
                id='gen_rates_builder',
                item_id_getter=lambda x: x[1],
                items='items',
                on_click=getters.choose_rate
            ),
            width=2
        ),
        SwitchTo(Format('{back}'), id='back', state=balanceSG.start),
        getter=getters.payment_menu_getter,
        state=balanceSG.payment_menu
    ),
    Window(
        Format('{text}'),
        Row(
            SwitchTo(Format('{yes}'), id='confirm_tokens_pay', state=balanceSG.choose_payment_menu),
            SwitchTo(Format('{back}'), id='back_payment_menu', state=balanceSG.payment_menu),
        ),
        getter=getters.tokens_confirm_getter,
        state=balanceSG.tokens_confirm
    ),
    Window(
        Format('{text}'),
        Column(
            SwitchTo(Format('{card_pay}'), id='card_pay_switcher', state=balanceSG.card_payment),
            SwitchTo(Format('{crypto_pay}'), id='crypto_pay_switcher', state=balanceSG.crypto_payment),
        ),
        SwitchTo(Format('{back}'), id='back', state=balanceSG.start),
        getter=getters.choose_payment_getter,
        state=balanceSG.choose_payment_menu
    ),
    Window(
        Format('{text}'),
        Url(Format('{url_text}'), id='url_button', url=Format('{url}')),
        Button(Format('{back}'), id='back_choose_payment', on_click=getters.back_choose_payment),
        getter=getters.card_pay_getter,
        state=balanceSG.card_payment
    ),
    Window(
        Format('{text}'),
        Url(Format('{url_text}'), id='url_button', url=Const('Ссылка')),
        SwitchTo(Format('{back}'), id='back_choose_payment', state=balanceSG.choose_payment_menu),
        getter=getters.crypto_pay_getter,
        state=balanceSG.crypto_payment
    ),
    Window(
        Format('{text}'),
        Column(
            SwitchTo(Format('{vip_switcher}'), id='vip_choose_switcher', state=balanceSG.vip_choose),
            SwitchTo(Format('{back}'), id='back', state=balanceSG.start),
        ),
        getter=getters.vip_menu_getter,
        state=balanceSG.vip_menu
    ),
    Window(
        Format('{text}'),
        Column(
            Button(Format('{one_day}'), id='one_day_toggle', on_click=getters.toggle_vip),
            Button(Format('{three_days}'), id='three_days_toggle', on_click=getters.toggle_vip),
            Button(Format('{one_week}'), id='week_toggle', on_click=getters.toggle_vip),
        ),
        SwitchTo(Format('{back}'), id='back_vip_menu', state=balanceSG.vip_menu),
        getter=getters.vip_choose_getter,
        state=balanceSG.vip_choose
    ),
    Window(
        DynamicMedia('media'),
        Format('{text}'),
        SwitchTo(Format('{back}'), id='back', state=balanceSG.start),
        getter=getters.history_menu_getter,
        state=balanceSG.history_menu
    ),
)