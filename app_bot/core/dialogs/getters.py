from aiogram.enums import ContentType
from core.database.models import Category, Estate, Post
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment
from settings import settings


async def get_welcome_msg(dialog_manager: DialogManager, **kwargs):
    welcome_post = await Post.get(id=settings.welcome_post_id)

    return {
        'caption': welcome_post.text,
        'photo': MediaAttachment(ContentType.PHOTO, url=welcome_post.photo_file_id)
    }


async def get_categories(dialog_manager: DialogManager, **kwargs):
    return {
        'budgets': await Category.filter(content_type=Category.ContentType.budget).all(),
        'commercial': await Category.filter(content_type=Category.ContentType.commercial).all()
    }


async def get_estates_by_category(dialog_manager: DialogManager, **kwargs) -> dict[str, list[Estate]]:
    current_page = await dialog_manager.find('estate_scroll').get_page()
    estates = await Estate.filter(parent_category_id=dialog_manager.start_data['category_id']).all()
    if not estates:
        raise ValueError

    current_estate = estates[current_page]

    media_content = None
    if current_estate.media_content:
        media_content = MediaAttachment(ContentType.PHOTO, url=current_estate.media_content)

    dialog_manager.dialog_data['current_estate_id'] = current_estate.id

    return {
        'pages': len(estates),
        'current_page': current_page + 1,
        'media_content': media_content,
        'description':  current_estate.description,
    }
