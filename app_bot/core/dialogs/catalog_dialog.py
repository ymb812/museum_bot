from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.kbd import PrevPage, NextPage, CurrentPage, Start, Column, StubScroll, Button, Row, \
    FirstPage, LastPage, SwitchTo, Select
from aiogram_dialog.widgets.input import TextInput
from core.dialogs.getters import get_exhibits_by_museum
from core.dialogs.callbacks import CallBackHandler
from core.states.main_menu import MainMenuStateGroup
from core.states.catalog import CatalogStateGroup
from core.utils.texts import _


statuses_select = Select(
    id='_status_select',
    items='statuses',
    item_id_getter=lambda item: item.name,
    text=Format(text='{item.value}'),
    on_click=CallBackHandler.selected_status,
)

catalog_dialog = Dialog(
    # exhibits
    Window(
        DynamicMedia(selector='media_content'),
        Format(text='{name}'),
        StubScroll(id='exhibit_scroll', pages='pages'),

        # cycle pager
        Row(
            LastPage(scroll='exhibit_scroll', text=Const('<'), when=F['current_page'] == 0),
            PrevPage(scroll='exhibit_scroll', when=F['current_page'] != 0),
            CurrentPage(scroll='exhibit_scroll'),
            NextPage(scroll='exhibit_scroll', when=F['current_page'] != F['pages'] - 1),
            FirstPage(scroll='exhibit_scroll', text=Const('>'), when=F['current_page'] == F['pages'] - 1),
            when=F['pages'] > 1,
        ),

        Column(
            statuses_select,
            Start(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=MainMenuStateGroup.menu)
        ),
        getter=get_exhibits_by_museum,
        state=CatalogStateGroup.status,
    ),

    # problem input
    Window(
        Const(text=_('INPUT_PROBLEM')),
        TextInput(
            id='input_problem',
            type_factory=str,
            on_success=CallBackHandler.entered_problem
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_catalog', state=CatalogStateGroup.status,
                 when=~F.get('start_data').get('inline_mode')),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_exhibit_page', state=CatalogStateGroup.exhibit,
                 when=F.get('start_data').get('inline_mode')),
        state=CatalogStateGroup.problem
    ),

    # exhibit from inline
    Window(
        DynamicMedia(selector='media_content'),
        Format(text='{name}'),
        Column(
            statuses_select,
            Start(Const(text=_('BACK_BUTTON')), id='go_to_inline', state=MainMenuStateGroup.exhibit)
        ),
        getter=get_exhibits_by_museum,
        state=CatalogStateGroup.exhibit
    ),
)
