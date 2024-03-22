from aiogram import F
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.kbd import PrevPage, NextPage, CurrentPage, Start, Column, StubScroll, Button, Row, \
    FirstPage, LastPage, SwitchTo
from aiogram_dialog.widgets.input import TextInput
from core.dialogs.getters import get_estates_by_category
from core.dialogs.callbacks import CallBackHandler
from core.states.main_menu import MainMenuStateGroup
from core.states.catalog import CatalogStateGroup
from core.utils.texts import _


catalog_dialog = Dialog(
    # estates
    Window(
        DynamicMedia(selector='media_content'),
        Format(text='{description}'),
        StubScroll(id='estate_scroll', pages='pages'),

        # cycle pager
        Row(
            LastPage(scroll='estate_scroll', text=Const('<'), when=F['current_page'] == 0),
            PrevPage(scroll='estate_scroll', when=F['current_page'] != 0),
            CurrentPage(scroll='estate_scroll'),
            NextPage(scroll='estate_scroll', when=F['current_page'] != F['pages'] - 1),  # if last: go to the first page
            FirstPage(scroll='estate_scroll', text=Const('>'), when=F['current_page'] == F['pages'] - 1),
            when=F['pages'] > 1,
        ),

        Column(
            SwitchTo(
                Const(text=_('PRESENTATION_BUTTON')), id='current_estate_id', state=CatalogStateGroup.get_presentation
            ),
            Start(
                Const(text=_('BACK_BUTTON')),
                id='go_to_budget',
                state=MainMenuStateGroup.gab,
                when=F['start_data']['came_from'] == 'budget',
            ),  # back to budget

            Start(
                Const(text=_('BACK_BUTTON')),
                id='go_to_commercial',
                state=MainMenuStateGroup.commercial,
                when=F['start_data']['came_from'] == 'commercial',
            ),  # back to commercial
        ),

        getter=get_estates_by_category,
        state=CatalogStateGroup.product_interaction,
    ),

    # get_presentation
    Window(
        Const(text=_('INPUT_PHONE')),
        TextInput(
            id='input_phone',
            type_factory=str,
            on_success=CallBackHandler.entered_phone
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_catalog', state=CatalogStateGroup.product_interaction),
        state=CatalogStateGroup.get_presentation
    ),
)
