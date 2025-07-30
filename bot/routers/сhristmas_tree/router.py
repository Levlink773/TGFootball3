from aiogram import Router
from .get_reward import get_reward_router

christmas_tree_router = Router()
christmas_tree_router.include_routers(
    get_reward_router
)
