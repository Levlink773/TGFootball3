from aiogram import Router

from bot.routers.blitz.add_energy_in_blitz import add_energy_in_match_router
from bot.routers.blitz.blitz_register_router import blitz_register_router
from bot.routers.blitz.reward_blitz_router import reward_blitz_router

blitz_router = Router()
blitz_router.include_routers(
    add_energy_in_match_router,
    blitz_register_router,
    reward_blitz_router
)