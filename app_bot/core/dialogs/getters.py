from aiogram.enums import ContentType
from core.database.models import User, Exhibit, Report, Museum, Post
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment
from settings import settings


async def get_welcome_msg(dialog_manager: DialogManager, **kwargs):
    welcome_post = await Post.get(id=settings.welcome_post_id)

    return {
        'caption': welcome_post.text,
        'photo': MediaAttachment(ContentType.PHOTO, url=welcome_post.photo_file_id)
    }


async def get_exhibits_by_museum(dialog_manager: DialogManager, **kwargs) -> dict[str, list[Exhibit]]:
    current_page = await dialog_manager.find('exhibit_scroll').get_page()
    museum_id = (await (await User.get_or_none(user_id=dialog_manager.event.from_user.id))).museum_id

    exhibits = await Exhibit.filter(museum_id=museum_id).all()
    if not exhibits:
        raise ValueError

    current_exhibit = exhibits[current_page]
    media_content = None
    if current_exhibit.media_content:
        media_content = MediaAttachment(ContentType.PHOTO, url=current_exhibit.media_content)

    statuses_dict = {status.name: status.value for status in Report.StatusType}
    statuses = [status for status in Report.StatusType]

    # data for CallbackHandler
    dialog_manager.dialog_data['museum_id'] = museum_id
    dialog_manager.dialog_data['pages'] = len(exhibits)
    dialog_manager.dialog_data['current_exhibit_id'] = current_exhibit.id
    dialog_manager.dialog_data['statuses_dict'] = statuses_dict

    return {
        'pages': len(exhibits),
        'current_page': current_page + 1,
        'media_content': media_content,
        'name': current_exhibit.name,
        'statuses': statuses
    }


async def get_bot_data(dialog_manager: DialogManager, **kwargs):
    return {
        'bot_username': (await dialog_manager.event.bot.get_me()).username
    }


async def get_exhibit_from_inline(dialog_manager: DialogManager, **kwargs):
    museum_id = (await (await User.get_or_none(user_id=dialog_manager.event.from_user.id))).museum_id
    exhibit = await Exhibit.get_or_none(id=dialog_manager.start_data['exhibit_id'], museum_id=museum_id)
    if not exhibit:
        raise ValueError

    media_content = None
    if exhibit.media_content:
        media_content = MediaAttachment(ContentType.PHOTO, url=exhibit.media_content)

    statuses_dict = {status.name: status.value for status in Report.StatusType}
    statuses = [status for status in Report.StatusType]

    # data for CallbackHandler
    dialog_manager.dialog_data['museum_id'] = museum_id
    dialog_manager.dialog_data['current_exhibit_id'] = exhibit.id
    dialog_manager.dialog_data['statuses_dict'] = statuses_dict

    return {
        'media_content': media_content,
        'name': exhibit.name,
        'statuses': statuses,
    }
