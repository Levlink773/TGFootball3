from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

from datetime import datetime, timedelta

from .service.get_new_clubs_league import NewClubLeaguRepository

from database.models.league_fight import LeagueFight

from league.user_sender import UserSender
from match.entities import MatchData, MatchClub
from match.core.match import Match
from match.core.manager import ClubMatchManager

from constants_leagues import config_new_club_league

class NewClubLeague:
    
    def __init__(self) -> None:
        self.scheduler_best_league =  AsyncIOScheduler()
        self._service = NewClubLeaguRepository()

    async def start_league(self):
        league_matchs = await self._service.get_matches()
        for match in league_matchs:
            await self.start_match(match)

        self.scheduler_best_league.start()
        
    async def start_match(self, match: LeagueFight) -> None:
        if match.time_to_start < datetime.now():
            return
        
        first_club = MatchClub(
            club_id = match.first_club.id
        )
        second_club = MatchClub(
            club_id = match.second_club.id
        )
        
        match_data = MatchData(
            first_club  = first_club,
            second_club = second_club,
            start_time  = match.time_to_start,
            match_id    = match.match_id,
            group_id    = match.group_id
        )
        match_ = Match(
            match_data = match_data,
            start_time = match.time_to_start
        )
        time_start_match = match.time_to_start.replace(
            hour = config_new_club_league.HOUR_TIME_START_MATCH,
            minute = 0
        )
        
        time_send_join_match_text = time_start_match - timedelta(minutes=15)
        
        user_sender = UserSender(
            match_id = match.match_id
        )
        ClubMatchManager.add_match(match_data)

        self.scheduler_best_league.add_job(
            func = user_sender.send_messages_to_users,
            trigger = DateTrigger(time_send_join_match_text),
            misfire_grace_time = 10
        )
        self.scheduler_best_league.add_job(
            func    = match_.start_match,
            trigger = DateTrigger(time_start_match),
            misfire_grace_time = 10
        )
        
class SchedulerNewClubLeague:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def start_scheduler(self):
        self.scheduler.add_job(
            func=NewClubLeague().start_league,
            trigger=config_new_club_league.TRIGGER_START_LEAGUE,
            misfire_grace_time=10
        )
        self.scheduler.start()