import logging
from tortoise.functions import Lower
from aiogram import types, Router
from core.database.models import User, Exhibit


logger = logging.getLogger(__name__)
router = Router(name='Inline-mode router')


@router.inline_query()
async def show_faq(inline_query: types.InlineQuery):
    museum_id = (await (await User.get_or_none(user_id=inline_query.from_user.id))).museum_id
    name = inline_query.query.lower()
    if len(name) == 0:
        return

    exhibits = await Exhibit.annotate(name_lower=Lower('name')).filter(museum_id=museum_id, name_lower__contains=name)

    results = []
    for i, exhibit in enumerate(exhibits):
        results.append(types.InlineQueryResultArticle(
            id=str(i),
            title=exhibit.name,
            input_message_content=types.InputTextMessageContent(
                message_text=str(exhibit.id),
                parse_mode='HTML',
            )
        ))

    await inline_query.answer(results, is_personal=True, cache_time=1)
