from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware, types


class PrivateChatMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: types.TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        chat: types.Chat = data['event_chat']
        if chat.type != 'private':
            return

        return await handler(event, data)
