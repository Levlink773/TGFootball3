from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

from datetime import datetime

from best_club_league.service.get_best_league_match import BestClubLeagueMatchService

from database.models.league_fight import LeagueFight

from league.user_sender import UserSender
from match.entities import MatchData, MatchClub
from match.core.match import Match
from match.core.manager import ClubMatchManager

from constants import START_DAY_BEST_LEAGUE

class BestClubLeague:
    
    def __init__(self) -> None:
        self.scheduler_best_league =  AsyncIOScheduler()
        self.best_league_service = BestClubLeagueMatchService()
        
    async def start_best_league(self):
        await self._start_league()
        
    async def _start_league(self):
        league_matchs = await self.best_league_service.get_matches()

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
        time_send_join_match_text = match.time_to_start.replace(
            hour = 20,
            minute = 20
        )
        time_start_match = match.time_to_start.replace(
            hour = 21,
            minute = 0
        )
        
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
        
class SchedulerBestClubtLeague:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def start_scheduler(self):
        self.scheduler.add_job(
            func=BestClubLeague().start_best_league,
            trigger=CronTrigger(day=START_DAY_BEST_LEAGUE, hour=8, minute=0),
            misfire_grace_time=10
        )
        self.scheduler.start()