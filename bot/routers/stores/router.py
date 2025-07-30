from aiogram import Router
from .items.items_store import items_store_router
from .items.exclusive_item_store import luxe_items_store_router
from .menu_stores import menu_magazine_router
from .box.box_handler import open_box_roter
from .bank.buy_money import bank_router
from .vip_pass.buy_vip_pass import vip_pass_router
from .change_position.change_position import change_position_router
from .energy.buy_energy import buy_energy_router

magazine_main_router = Router()
magazine_main_router.include_routers(
    menu_magazine_router,
    items_store_router,
    open_box_roter,
    luxe_items_store_router,
    bank_router,
    vip_pass_router,
    change_position_router,
    buy_energy_router
)