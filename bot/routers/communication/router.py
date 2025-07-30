from aiogram import Router
from .communication import communication_router

communication_main_router = Router()
communication_main_router.include_routers(
    communication_router
)