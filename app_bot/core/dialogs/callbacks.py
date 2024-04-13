from aiogram.types import CallbackQuery, Message, LabeledPrice
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select, SwitchPage
from core.states.catalog import CatalogStateGroup
from core.states.main_menu import MainMenuStateGroup
from core.database.models import Exhibit, Report
from core.utils.texts import _
from settings import settings


async def switch_page(dialog_manager: DialogManager, scroll_id: str, message: Message):
    # switch page
    scroll: ManagedScroll = dialog_manager.find(scroll_id)
    current_page = await scroll.get_page()
    if current_page == dialog_manager.dialog_data['pages'] - 1:
        # next_page = 0
        # go back to the menu
        await message.answer(text='Осмотр завершен, спасибо!')
        await dialog_manager.start(MainMenuStateGroup.menu)
        return
    else:
        next_page = current_page + 1
    await scroll.set_page(next_page)


class CallBackHandler:
    @classmethod
    async def selected_status(
            cls,
            callback: CallbackQuery,
            widget: Select,
            dialog_manager: DialogManager,
            item_id: str,
    ):

        status = dialog_manager.dialog_data['statuses_dict'][item_id]
        dialog_manager.dialog_data['status'] = status

        # go to next page if 'work'
        if item_id == 'work':
            # create report
            await Report.create(
                status=dialog_manager.dialog_data['status'],
                exhibit_id=dialog_manager.dialog_data['current_exhibit_id'],
                museum_id=dialog_manager.dialog_data['museum_id'],
                creator_id=callback.from_user.id
            )

            if dialog_manager.start_data and dialog_manager.start_data.get('inline_mode'):  # go back to inline
                await dialog_manager.start(MainMenuStateGroup.exhibit)
                return

            # switch page
            await switch_page(dialog_manager=dialog_manager, scroll_id='exhibit_scroll', message=callback.message)

        else:
            await dialog_manager.switch_to(CatalogStateGroup.problem)


    @staticmethod
    async def entered_problem(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: str,
    ):
        dialog_manager.dialog_data['problem'] = value

        # create report
        await Report.create(
            status=dialog_manager.dialog_data['status'],
            description=value.strip(),
            exhibit_id=dialog_manager.dialog_data['current_exhibit_id'],
            museum_id=dialog_manager.dialog_data['museum_id'],
            creator_id=message.from_user.id
        )

        if dialog_manager.start_data and dialog_manager.start_data.get('inline_mode'):
            await dialog_manager.start(MainMenuStateGroup.exhibit)  # go back to inline
        else:
            await dialog_manager.switch_to(state=CatalogStateGroup.status)  # go back to the catalog

            # switch page
            await switch_page(dialog_manager=dialog_manager, scroll_id='exhibit_scroll', message=message)


    @staticmethod
    async def entered_exhibit_id(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value: int,
    ):
        await dialog_manager.start(CatalogStateGroup.exhibit, data={'inline_mode': True, 'exhibit_id': value})
