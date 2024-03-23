from core.handlers.welcome import router as welcome_router
from core.handlers.admin import router as admin_router
from core.handlers.inline_mode import router as inline_router


routers = [welcome_router, admin_router, inline_router]
