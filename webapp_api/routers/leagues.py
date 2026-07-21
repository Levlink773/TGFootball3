from fastapi import APIRouter, Depends
from aiogram.utils.web_app import WebAppInitData

from constants_leagues import TypeLeague, GetConfig, NAMES_LEAGUES
from bot.utils.get_top_24_club_by_league import get_top_24_clubs

from services.league_services.default_league_service import DefaultLeagueService
from services.league_services.best_league_service import BestLeagueService
from services.league_services.new_clubs_league_service import NewClubsLeagueService
from services.league_services.top_20_club_league_service import Top20ClubLeagueService

from utils.redis_cache import cached_json
from webapp_api.auth import auth_user

leagues_router = APIRouter()

LEAGUE_SERVICES = {
    TypeLeague.DEFAULT_LEAGUE: DefaultLeagueService,
    TypeLeague.TOP_20_CLUB_LEAGUE: Top20ClubLeagueService,
    TypeLeague.NEW_CLUB_LEAGUE: NewClubsLeagueService,
    TypeLeague.BEST_LEAGUE: BestLeagueService,
}


async def _build_leagues() -> dict:
    leagues = []
    for type_league, service in LEAGUE_SERVICES.items():
        config = GetConfig.get_config(type_league)
        fights = await service.get_month_league() or []
        standings = [
            {
                "club_id": row["club_id"],
                "club_name": row["club_name"],
                "points": row["points"],
                "goals_scored": row["goals_scored"],
                "goals_conceded": row["goals_conceded"],
                "goal_difference": row["goal_difference"],
                "total_power": round(row["total_power"], 2),
            }
            for row in get_top_24_clubs(fights)
        ]
        leagues.append({
            "type": type_league.value,
            "name": NAMES_LEAGUES[type_league],
            "day_start": config.DAY_START,
            "day_end": config.DAY_END,
            "match_hour": config.HOUR_TIME_START_MATCH,
            "is_active": config.league_is_active,
            "standings": standings,
        })
    return {"leagues": leagues}


@leagues_router.get("/leagues")
async def get_leagues(auth: WebAppInitData = Depends(auth_user)):
    return await cached_json("webapp:leagues", ttl=60, producer=_build_leagues)
