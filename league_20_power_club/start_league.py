from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

from datetime import datetime

from league_20_power_club.service.get_best_club_match import BestClubLeagueMatchService
from league_20_power_club.service.generate_last_match import GenerateLastMatchService
from league_20_power_club.utils.sender_info import SendEndMatch, SendCongratulationEndMatch

from database.models.league_fight import LeagueFight

from match.entities import MatchData, MatchClub
from match.core.match import Match
from match.core.manager import ClubMatchManager

from services.league_services.league_service import LeagueService


from league.user_sender import UserSender

from constants import (
    END_MATCH_TOP_20_CLUB, 
    SEND_GONGRATULATION_END_BEST_MATCH,
    START_DAY_BEST_20_CLUB_LEAGUE   
)

class Best20ClubLeague:
    
    def __init__(self) -> None:
        self.scheduler_best_league =  AsyncIOScheduler()
        self.best_league_service = BestClubLeagueMatchService()
        self.last_match_service = GenerateLastMatchService()
        
    async def start_best_league(self):
        await self._start_league()
        
        self.scheduler_best_league.add_job(
            func = self._start_end_match,
            trigger = END_MATCH_TOP_20_CLUB
        )
        self.scheduler_best_league.start()

        
    async def _start_end_match(self):
        end_match: LeagueFight = await self.last_match_service.get_last_match()
        end_match: LeagueFight = await LeagueService.get_league_fight(
            match_id = end_match.match_id
        )
        sender_end_match = SendEndMatch(
            clubs = self.last_match_service.all_clubs,
            best_2_clubs = [
                end_match.first_club,
                end_match.second_club
            ]
        )
        await sender_end_match.send_info_to_clubs()

        send_congratulation = SendCongratulationEndMatch()
        self.scheduler_best_league.add_job(
            func = send_congratulation.send_info_to_clubs,
            trigger = SEND_GONGRATULATION_END_BEST_MATCH
            )
        
        await self.start_match(end_match)
        
    async def _start_league(self):
        league_matchs = await self.best_league_service.get_matches()

        for match in league_matchs:
            await self.start_match(match)


    
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
            hour = 16,
            minute = 15
        )

        
        time_start_match = match.time_to_start.replace(
            hour = 17,
            minute = 0
        )
        ClubMatchManager.add_match(match_data)

        user_sender = UserSender(
            match_id = match.match_id
        )
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
        
        
class SchedulerBest20ClubLeague:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def start_scheduler(self):
        self.scheduler.add_job(
            func=Best20ClubLeague().start_best_league,
            trigger=CronTrigger(day=START_DAY_BEST_20_CLUB_LEAGUE, hour=8, minute=0),
            misfire_grace_time=10
        )
        self.scheduler.start()
