from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Column, Url, SwitchTo, Start
from aiogram_dialog.widgets.media import DynamicMedia
from core.states.main_menu import MainMenuStateGroup
from core.states.catalog import CatalogStateGroup
from core.utils.texts import _
from core.dialogs.custom_content import CustomPager
# from core.dialogs.callbacks import CallBackHandler
# from core.dialogs.getters import get_categories, get_welcome_msg
from settings import settings


main_menu_dialog = Dialog(
    # menu
    Window(
        Const(text=_('PICK_ACTION')),
        Column(
            Start(Const(text=_('REPORT_BUTTON')), id='go_to_report', state=CatalogStateGroup.status),
            SwitchTo(Const(text=_('EXHIBIT_BUTTON')), id='go_to_exhibit', state=MainMenuStateGroup.exhibit),
            Url(
                Const(text=_('SUPPORT_BUTTON')),
                Const(text=settings.admin_chat_link),
            )
        ),
        state=MainMenuStateGroup.menu,
    ),
)
