import logging
from aiogram import Bot, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram_dialog import DialogManager, StartMode
from core.states.main_menu import MainMenuStateGroup
from core.utils.texts import set_user_commands, set_admin_commands, _
from core.database.models import User
from settings import settings


logger = logging.getLogger(__name__)
router = Router(name='Start router')


@router.message(Command(commands=['start']), StateFilter(None))
async def start_handler(message: types.Message, bot: Bot, state: FSMContext, dialog_manager: DialogManager,
                        command: CommandObject):
    user = await User.get_or_none(user_id=message.from_user.id)
    if not command.args and not user:  # ignore start w/o link from non-users
        return

    if command.args == settings.admin_password.get_secret_value():
        # add admin
        await state.clear()
        await message.answer(text=_('NEW_ADMIN_TEXT'))

        await User.update_admin_data(user_id=message.from_user.id, username=message.from_user.username, status='admin')
        await set_admin_commands(bot=bot, scope=types.BotCommandScopeChat(chat_id=message.from_user.id))
        return

    elif command.args:
        # add worker
        link = settings.bot_link + command.args
        user = await User.get_or_none(link=link)
        if not user:  # ignore start w/o link from non-users
            return

        # save tg data and delete link
        user.user_id = message.from_user.id
        user.username = message.from_user.username
        user.link = None
        await user.save()


    await state.clear()
    if user.status == 'admin':
        await set_admin_commands(bot=bot, scope=types.BotCommandScopeChat(chat_id=message.from_user.id))
    else:
        await set_user_commands(bot=bot, scope=types.BotCommandScopeChat(chat_id=message.from_user.id))

    # send main menu
    await dialog_manager.start(state=MainMenuStateGroup.menu, mode=StartMode.RESET_STACK)
