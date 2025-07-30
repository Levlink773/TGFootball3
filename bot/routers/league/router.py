from aiogram import Router
from .join_to_fight_handler import join_to_fight_router
from .league_handler import league_router
from .add_energy_in_match import add_energy_in_match_router
from .beast_league import best_league_router 
from .best_20_club_league import best_20_club_league_router
from .new_club_league import new_club_league_router
from .menu_league import menu_league_router

league_main_router = Router()
league_main_router.include_routers(
    menu_league_router,
    join_to_fight_router,
    best_league_router,
    league_router,
    add_energy_in_match_router,
    best_20_club_league_router,
    new_club_league_router
)