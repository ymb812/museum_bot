from aiogram.types import CallbackQuery, Message, LabeledPrice
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select
from core.states.catalog import CatalogStateGroup
from core.database.models import Estate
from core.utils.texts import _
from settings import settings


class CallBackHandler:
    __dialog_data_key = ''
    __switch_to_state = None

    @classmethod
    async def selected_content(
            cls,
            callback: CallbackQuery,
            widget: Select,
            dialog_manager: DialogManager,
            item_id: str,
    ):
        if '_budget_' in callback.data:
            cls.__dialog_data_key = 'category_id'
            cls.__switch_to_state = CatalogStateGroup.product_interaction
            came_from = 'budget'  # for back button in catalog

        if '_commercial_' in callback.data:
            cls.__dialog_data_key = 'category_id'
            cls.__switch_to_state = CatalogStateGroup.product_interaction
            came_from = 'commercial'  # for back button in catalog

        dialog_manager.dialog_data['came_from'] = came_from
        dialog_manager.dialog_data[cls.__dialog_data_key] = item_id
        await dialog_manager.start(cls.__switch_to_state, data=dialog_manager.dialog_data)


    @staticmethod
    async def entered_phone(
            message: Message,
            widget: ManagedTextInput,
            dialog_manager: DialogManager,
            value,
    ):
        dialog_manager.dialog_data['phone'] = value
        estate = await Estate.get_or_none(id=dialog_manager.dialog_data['current_estate_id'])

        # send question to admin
        if message.from_user.username:
            username = f'@{message.from_user.username}'
        else:
            username = f'<a href="tg://user?id={message.from_user.id}">ссылка</a>'
        await dialog_manager.middleware_data['bot'].send_message(
            chat_id=settings.admin_chat_id,
            text=_('REQUEST_FROM_USER', username=username, phone=value, estate_id=estate.id),
        )

        if estate.presentation:
            await message.answer_document(document=estate.presentation)
        await dialog_manager.switch_to(state=CatalogStateGroup.product_interaction)  # go back to the catalog
