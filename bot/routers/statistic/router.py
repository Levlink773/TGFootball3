from aiogram import Router

from .routers.statistic_club_league import menu_choice_league_club_router
from .routers.menu_choice_statistic import menu_statistic_router
from .routers.statistic_matches.matches_by_league import menu_select_type_group_router
from .routers.statistic_matches.matches_by_top_20_league import menu_choice_type_top_20_group_router
from .routers.statistic_matches.menu_statistic_matches import menu_choice_type_league_club_router
from .routers.statistic_matches.statistic_matches import statistics_matches_router


statistic_router = Router()
statistic_router.include_routers(
    menu_statistic_router,
    menu_choice_league_club_router,
    menu_choice_type_league_club_router,
    statistics_matches_router,
    menu_select_type_group_router,
    menu_choice_type_top_20_group_router
)