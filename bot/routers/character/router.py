from aiogram import Router
from .menu_character import menu_character_router
from .items_character import items_character_router

character_router = Router()
character_router.include_routers(
    menu_character_router,
    items_character_router
)