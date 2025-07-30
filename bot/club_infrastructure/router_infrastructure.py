from aiogram import Router
from .routers.menu_infrastructure import start_menu_infrastructure_router
from .routers.select_infrastructure import select_infrastructure_router
from .routers.update_level_infrastructure import update_level_infrastructure_router
from .routers.info_destribute_points import info_desrtibute_points_router

router_infrastructure = Router()

router_infrastructure.include_routers(
    start_menu_infrastructure_router,
    select_infrastructure_router,
    update_level_infrastructure_router,
    info_desrtibute_points_router
)