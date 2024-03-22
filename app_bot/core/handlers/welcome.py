import logging
from aiogram import Bot, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter, CommandObject
from aiogram_dialog import DialogManager, StartMode
from core.states.main_menu import MainMenuStateGroup
from core.utils.texts import set_user_commands, set_admin_commands, _
from core.database.models import User, Post
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
        await state.clear()
        await message.answer(text=_('NEW_ADMIN_TEXT'))

        await User.set_status(user_id=message.from_user.id, status='admin')
        await set_admin_commands(bot=bot, scope=types.BotCommandScopeChat(chat_id=message.from_user.id))
        return
    else:
        # check link from db and delete
        link = settings.bot_link + command.args
        print(link)
        user = await User.get_or_none(link=link)
        if not user:
            return

        # TODO: DELETE USED LINK - HOW? MB JUST DELETE LINK OR MB DONT CARE?

    await User.update_data(
        link=link,
        user_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        username=message.from_user.username,
        language_code=message.from_user.language_code,
        is_premium=message.from_user.is_premium,
    )


    await state.clear()

    user = await User.get(user_id=message.from_user.id)
    if user.status == 'admin':
        await set_admin_commands(bot=bot, scope=types.BotCommandScopeChat(chat_id=message.from_user.id))
    else:
        await set_user_commands(bot=bot, scope=types.BotCommandScopeChat(chat_id=message.from_user.id))

    # send main menu
    await dialog_manager.start(state=MainMenuStateGroup.menu, mode=StartMode.RESET_STACK)
