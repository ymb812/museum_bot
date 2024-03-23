from aiogram import F
from aiogram.types import CallbackQuery, Message, LabeledPrice
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select, SwitchPage
from core.states.catalog import CatalogStateGroup
from core.database.models import Exhibit, Report
from core.utils.texts import _
from settings import settings


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
            )

            scroll: ManagedScroll = dialog_manager.find('exhibit_scroll')
            current_page = await scroll.get_page()
            if current_page == dialog_manager.dialog_data['pages'] - 1:
                next_page = 0
            else:
                next_page = current_page + 1

            await scroll.set_page(next_page)

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
        )

        await dialog_manager.switch_to(state=CatalogStateGroup.status)  # go back to the catalog
