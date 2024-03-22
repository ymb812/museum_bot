from aiogram import Bot
from aiogram.utils.i18n import I18n
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Column, Url, SwitchTo, Select
from aiogram_dialog.widgets.media import DynamicMedia
from core.states.main_menu import MainMenuStateGroup
from core.utils.texts import _
from core.dialogs.custom_content import CustomPager
from core.dialogs.callbacks import CallBackHandler
from core.dialogs.getters import get_categories, get_welcome_msg
from settings import settings


bot = Bot(settings.bot_token.get_secret_value(), parse_mode='HTML')
i18n = I18n(path='locales', default_locale='ru', domain='messages')
i18n.set_current(i18n)


main_menu_dialog = Dialog(
    # menu
    Window(
        DynamicMedia(selector='photo'),
        Format(text='{caption}'),
        Column(
            SwitchTo(Const(text=_('GAB_BUTTON')), id='go_to_gab', state=MainMenuStateGroup.gab),
            SwitchTo(Const(text=_('ESTATE_BUTTON')), id='go_to_commercial', state=MainMenuStateGroup.commercial),
            Url(
                Const(text=_('SUPPORT_BUTTON')),
                Const(text=settings.admin_chat_link),
            )
        ),
        getter=get_welcome_msg,
        state=MainMenuStateGroup.menu,
    ),

    # budget
    Window(
        Const(text=_('PICK_BUDGET')),
        CustomPager(
            Select(
                id='_budget_select',
                items='budgets',
                item_id_getter=lambda item: item.id,
                text=Format(text='{item.name}'),
                on_click=CallBackHandler.selected_content,
            ),
            id='budget_group',
            height=settings.categories_per_page_height,
            width=settings.categories_per_page_width,
            hide_on_single_page=True,
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=MainMenuStateGroup.menu),
        getter=get_categories,
        state=MainMenuStateGroup.gab,
    ),

    # commercial
    Window(
        Const(text=_('PICK_COMMERCIAL')),
        CustomPager(
            Select(
                id='_commercial_select',
                items='commercial',
                item_id_getter=lambda item: item.id,
                text=Format(text='{item.name}'),
                on_click=CallBackHandler.selected_content,
            ),
            id='budget_group',
            height=settings.categories_per_page_height,
            width=settings.categories_per_page_width,
            hide_on_single_page=True,
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=MainMenuStateGroup.menu),
        getter=get_categories,
        state=MainMenuStateGroup.commercial,
    ),
)
