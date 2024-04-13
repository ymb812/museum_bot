import logging
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Select, Button
from core.states.catalog import CatalogStateGroup
from core.states.main_menu import MainMenuStateGroup
from core.database.models import Report, ReportSession, User
from core.excel.excel_generator import create_excel_after_checking


logger = logging.getLogger(__name__)


async def switch_page(dialog_manager: DialogManager, scroll_id: str, message: Message):
    # switch page
    scroll: ManagedScroll = dialog_manager.find(scroll_id)
    current_page = await scroll.get_page()
    session_id = dialog_manager.start_data.get('session_id')  # to indentify exhibits checks

    if current_page == dialog_manager.dialog_data['pages'] - 1:
        # go back to the menu
        await message.answer(text='Осмотр завершен, спасибо!')
        await dialog_manager.start(MainMenuStateGroup.menu)

        # send reports file to users
        reports_receivers = await User.filter(is_reports_receiver=True).all()
        reports_by_session = await Report.filter(session_id=session_id).all()

        try:
            file_in_memory, is_empty = await create_excel_after_checking(reports=reports_by_session)
        except Exception as e:
            logger.info(f'Error in creating file after checking', exc_info=e)

        try:
            if not is_empty:  # send file if there are any reports
                file = file_in_memory.read()
                for user in reports_receivers:
                    await dialog_manager.event.bot.send_document(
                        chat_id=user.user_id,
                        document=BufferedInputFile(file=file, filename='Отчеты.xlsx'),
                    )
        except Exception as e:
            logger.info(f'Error in sending file after checking', exc_info=e)

        return

    else:
        next_page = current_page + 1

    await scroll.set_page(next_page)


class CallBackHandler:
    @classmethod
    async def start_checking(
            cls,
            callback: CallbackQuery,
            widget: Button,
            dialog_manager: DialogManager,
    ):
        # create new session
        session = await ReportSession.create(creator_id=callback.from_user.id)
        await dialog_manager.start(state=CatalogStateGroup.status, data={'session_id': session.id})


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
                creator_id=callback.from_user.id,
                session_id=dialog_manager.start_data.get('session_id'),
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
            creator_id=message.from_user.id,
            session_id=dialog_manager.start_data.get('session_id'),
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
