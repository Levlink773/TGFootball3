from aiogram import Router
from .my_club import my_club_router
from .create_club import create_club_router
from .find_club import find_club_router
from .club_owner_optinos import owner_option_club_router
from .research_club import research_club_router
from .custom_stadion import custom_stadion_router
from .club_invoices import club_invoices_router

club_router = Router()
club_router.include_routers(
    my_club_router,
    create_club_router,
    find_club_router,
    owner_option_club_router,
    research_club_router,
    custom_stadion_router,
    club_invoices_router
)