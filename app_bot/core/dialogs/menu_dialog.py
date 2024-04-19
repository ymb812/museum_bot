from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Column, Url, SwitchTo, Button
from core.states.main_menu import MainMenuStateGroup
from core.utils.texts import _
from core.dialogs.callbacks import CallBackHandler
from core.dialogs.getters import get_bot_data
from settings import settings


main_menu_dialog = Dialog(
    # menu
    Window(
        Const(text=_('PICK_ACTION')),
        Column(
            Button(Const(text=_('REPORT_BUTTON')), id='go_to_report', on_click=CallBackHandler.start_checking),
            SwitchTo(Const(text=_('EXHIBIT_BUTTON')), id='go_to_exhibit', state=MainMenuStateGroup.exhibit),
            Url(
                Const(text=_('SUPPORT_BUTTON')),
                Const(text=settings.admin_chat_link),
            )
        ),
        state=MainMenuStateGroup.menu,
    ),

    # exhibit input
    Window(
        Format(text=_('INPUT_EXHIBIT', bot_username='{bot_username}')),
        TextInput(
            id='input_exhibit',
            type_factory=int,
            on_success=CallBackHandler.entered_exhibit_id
        ),
        SwitchTo(Const(text=_('BACK_BUTTON')), id='go_to_menu', state=MainMenuStateGroup.menu),
        getter=get_bot_data,
        state=MainMenuStateGroup.exhibit
    ),
)
