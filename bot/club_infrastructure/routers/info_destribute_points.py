from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.club_infrastructure.config import POINTS_FROM_DISTRIBUTE_FROM_LEAGUE
from bot.club_infrastructure.constans import PHOTO_DESTRIBUTE_POINTS

from best_club_league.types import LeagueRanking
from constants_leagues import TypeLeague

info_desrtibute_points_router = Router()

def format_league_points() -> str:
    points = POINTS_FROM_DISTRIBUTE_FROM_LEAGUE

    league_names = {
        TypeLeague.BEST_LEAGUE: "🏆 <b>Єврокубки</b>",
        TypeLeague.DEFAULT_LEAGUE: "🏆 <b>Національний Чемпіонат</b>",
        TypeLeague.TOP_20_CLUB_LEAGUE: "🏆 <b>Національний Кубок України</b>",
    }

    best_league_text = "\n".join(
        f"- {group.value}: 🥇 {pts[0]} очок, 🥈 {pts[1]} очок, 🥉 {pts[2]} очок"
        for group, pts in points[TypeLeague.BEST_LEAGUE].items()
    )

    def format_points(league: TypeLeague) -> str:
        return f"- 🥇 {points[league][0]} очок, 🥈 {points[league][1]} очок, 🥉 {points[league][2]} очок"

    return f"""
<b>🏆 Розподіл очок у лігах</b>

🔹 {league_names[TypeLeague.BEST_LEAGUE]}
{best_league_text}

🔹 {league_names[TypeLeague.DEFAULT_LEAGUE]}
{format_points(TypeLeague.DEFAULT_LEAGUE)}

🔹 {league_names[TypeLeague.TOP_20_CLUB_LEAGUE]}
{format_points(TypeLeague.TOP_20_CLUB_LEAGUE)}
"""

LEAGUE_POINTS_DESCRIPTION = format_league_points()



@info_desrtibute_points_router.callback_query(
    F.data == "info_desrtibute_club_points"
)
async def start_command_handler(
    query: CallbackQuery,
):
    await query.message.answer_photo(
        photo = PHOTO_DESTRIBUTE_POINTS,
        caption = LEAGUE_POINTS_DESCRIPTION,
    )   