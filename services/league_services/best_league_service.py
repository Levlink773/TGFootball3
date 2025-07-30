from datetime import datetime

from sqlalchemy import select, or_, and_, func, case, desc

from constants_leagues import TypeLeague, GetConfig

from database.models.league_fight import LeagueFight
from database.models.club import Club

from database.session import get_session

from .league_service import LeagueService


class BestLeagueService(LeagueService):
    type_league = TypeLeague.BEST_LEAGUE
    config = GetConfig.get_config(TypeLeague.BEST_LEAGUE)
    
    @classmethod
    async def get_top_24_clubs(cls) -> list[Club]:
        now = datetime.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month_20th = now.replace(day=20, hour=0, minute=0, second=0, microsecond=0)

        async for session in get_session():
            async with session.begin():
                # Подзапрос для очков, забитых и пропущенных голов для первой и второй команды
                first_team_points = (
                    select(
                        LeagueFight.first_club_id.label("club_id"),
                        func.sum(
                            case(
                                (LeagueFight.goal_first_club > LeagueFight.goal_second_club, 3),
                                (LeagueFight.goal_first_club == LeagueFight.goal_second_club, 1),
                                else_=0,
                            )
                        ).label("points"),
                        func.sum(LeagueFight.goal_first_club).label("goals_scored"),
                        func.sum(LeagueFight.goal_second_club).label("goals_conceded")
                    )
                    .where(LeagueFight.time_to_start >= start_of_month)
                    .where(LeagueFight.time_to_start <= end_of_month_20th)
                    .group_by(LeagueFight.first_club_id)
                )

                second_team_points = (
                    select(
                        LeagueFight.second_club_id.label("club_id"),
                        func.sum(
                            case(
                                (LeagueFight.goal_second_club > LeagueFight.goal_first_club, 3),
                                (LeagueFight.goal_second_club == LeagueFight.goal_first_club, 1),
                                else_=0,
                            )
                        ).label("points"),
                        func.sum(LeagueFight.goal_second_club).label("goals_scored"),
                        func.sum(LeagueFight.goal_first_club).label("goals_conceded")
                    )
                    .where(LeagueFight.time_to_start >= start_of_month)
                    .where(LeagueFight.time_to_start <= end_of_month_20th)
                    .group_by(LeagueFight.second_club_id)
                )
                combined_points = first_team_points.union_all(second_team_points).subquery()
                aggregated_points = (
                    select(
                        combined_points.c.club_id,
                        func.sum(combined_points.c.points).label("total_points"),
                        func.sum(combined_points.c.goals_scored).label("total_goals_scored"),
                        func.sum(combined_points.c.goals_conceded).label("total_goals_conceded"),
                        (func.sum(combined_points.c.goals_scored) - func.sum(combined_points.c.goals_conceded)).label("goal_difference")
                    )
                    .group_by(combined_points.c.club_id)
                    .subquery()
                )
                final_query = (
                    select(Club)
                    .join(aggregated_points, aggregated_points.c.club_id == Club.id)
                    .order_by(
                        aggregated_points.c.total_points.desc(),
                        aggregated_points.c.goal_difference.desc(),
                        aggregated_points.c.total_goals_scored.desc()
                    )
                    .limit(24)
                )

                result = await session.execute(final_query)
                return [club for club, in result]
