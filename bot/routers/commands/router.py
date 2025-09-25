from aiogram import Router

from .admins_functional.cleanup_club_router import club_router
from .admins_functional.get_logging_file import get_logger_router
from .admins_functional.info_last_pvp import info_last_pvp_router
from .admins_functional.refresh_router import refresh_router
from .instruction import send_instruction_router
from .start import start_router

commands_router = Router()
commands_router.include_routers(
    start_router,
    send_instruction_router,
    get_logger_router,
    info_last_pvp_router,
    refresh_router,
    club_router
)
