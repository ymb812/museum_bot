import json
import logging
import asyncio
from aiogram import types, Router, F, Bot
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from broadcaster import Broadcaster
from core.database.models import User, Report, Museum
from core.keyboards.inline import mailing_kb
from core.states.mailing import MailingStateGroup
from core.utils.texts import _, set_admin_commands
from core.excel.excel_generator import create_main_reports_excel
from settings import settings


logger = logging.getLogger(__name__)
router = Router(name='Admin commands router')


# ez to get id while developing
@router.channel_post(Command(commands=['init']))
@router.message(Command(commands=['init']))
async def init_for_id(message: types.Message):
    await message.delete()
    msg = await message.answer(text=f'<code>{message.chat.id}</code>')
    await asyncio.sleep(2)
    await msg.delete()


# admin login
@router.message(Command(commands=['admin']))
async def admin_login(message: types.Message, state: FSMContext, command: CommandObject, bot: Bot):
    if command.args == settings.admin_password.get_secret_value():
        await state.clear()
        await message.answer(text=_('NEW_ADMIN_TEXT'))
        await User.update_admin_data(user_id=message.from_user.id, username=message.from_user.username, status='admin')
        await set_admin_commands(bot=bot, scope=types.BotCommandScopeChat(chat_id=message.from_user.id))


@router.message(Command(commands=['send']))
async def start_of_mailing(message: types.Message, state: FSMContext):
    user = await User.get(user_id=message.from_user.id)
    if user.status != 'admin':
        return

    await message.answer(_('INPUT_MAILING_CONTENT'))
    await state.set_state(MailingStateGroup.content_input)


@router.message(MailingStateGroup.content_input)
async def confirm_mailing(message: types.Message, state: FSMContext):
    await message.answer(text=_('CONFIRM_MAILING'), reply_markup=mailing_kb())
    await state.update_data(content=message.model_dump_json(exclude_defaults=True))


@router.callback_query(F.data == 'start_mailing', MailingStateGroup.content_input)
async def admin_team_approve_handler(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    # cuz command is only for 'admin'
    user = await User.get(user_id=callback.from_user.id)
    users_amount = len(await User.all())

    state_data = await state.get_data()

    text = _('MAILING_HAS_BEEN_STARTED', admin_username=callback.from_user.username)
    await callback.message.answer(text=text)

    sent_amount = await Broadcaster.send_content_to_users(bot=bot,
                                                          message=types.Message(**json.loads(state_data['content'])))
    await state.clear()

    await callback.message.answer(text=_('MAILING_IS_COMPLETED', users_amount=users_amount, sent_amount=sent_amount))


@router.message(Command(commands=['stats']))
async def excel_stats(message: types.Message):
    # cuz command is only for 'admin'
    user = await User.get(user_id=message.from_user.id)
    if user.status != 'admin':
        return

    # get reports for each museum
    museums = await Museum.all()
    for museum in museums:
        reports = await Report.filter(museum_id=museum.id).all()
        if reports:
            file_in_memory = await create_main_reports_excel(reports=reports)
            await message.answer_document(
                document=types.BufferedInputFile(file_in_memory.read(), filename=f'Отчет по {museum.name}.xlsx'),
            )


# get file_id for broadcaster
@router.message(F.video | F.video_note | F.photo | F.audio | F.animation | F.sticker | F.document)
async def get_hash(message: types.Message):
    if (await User.get(user_id=message.from_user.id)).status != 'admin':
        return

    if message.video:
        hashsum = message.video.file_id
    elif message.video_note:
        hashsum = message.video_note.file_id
    elif message.photo:
        hashsum = message.photo[-1].file_id
    elif message.audio:
        hashsum = message.audio.file_id
    elif message.animation:
        hashsum = message.animation.file_id
    elif message.sticker:
        hashsum = message.sticker.file_id
    elif message.document:
        hashsum = message.document.file_id
    else:
        return

    await message.answer(f'<code>{hashsum}</code>')
