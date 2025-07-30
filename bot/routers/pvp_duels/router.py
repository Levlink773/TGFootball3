from aiogram import Router
from .find_user_duel import find_user_duel_router
from .procesing_duel import procesing_duel_router

duel_main_router = Router()
duel_main_router.include_routers(
    find_user_duel_router,
    procesing_duel_router
)