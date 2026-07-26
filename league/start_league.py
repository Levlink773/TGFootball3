from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger

from database.models.league_fight import LeagueFight

from constants import START_DAY_DEFAULT_LEAGUE

from match.entities import MatchData, MatchClub
from match.core.match import Match
from match.core.manager import ClubMatchManager

from league.user_sender import UserSender, schedule_match_reminders
from league.create_league.create_league_match import CreateDefaultLeagueMatches

from services.league_services.default_league_service import DefaultLeagueService 



TEST = False

class StartDefaultLeague:
    
    def __init__(self):
        self.scheduler_league = AsyncIOScheduler()
    
    async def setup_matches(self) -> None:
        matches = await DefaultLeagueService.get_month_league()
        if not matches:
            await CreateDefaultLeagueMatches().create_default_league_matches()
            matches = await DefaultLeagueService.get_month_league()
        await self._start_match(matches)
        
        self.scheduler_league.start()
            
    async def _start_match(self, matches: list[LeagueFight]) -> None:
        START_TEST = False
        for match in matches:
            if TEST:
                if self._is_my_club_test(match) and not START_TEST:
                    START_TEST = True
                    await self.schedule_match_start_test(match)
            else:
                await self.schedule_match_start(match)

    def _is_my_club_test(self, match: LeagueFight) -> bool:
        my_id = 6790393255
        first_characters_id = [character.characters_user_id for character in match.first_club.characters]
        second_characters_id = [character.characters_user_id for character in match.second_club.characters]
        return my_id in first_characters_id or my_id in second_characters_id
        
    async def schedule_match_start_test(self, match: LeagueFight):
        
        start_time_fight = datetime.now() + timedelta(minutes=1)
        start_time_sender = datetime.now()
        
        first_club = MatchClub(
            club_id = match.first_club.id
        )
        second_club = MatchClub(
            club_id = match.second_club.id
        )

        match_data = MatchData(
            match_id = match.match_id,
            group_id = match.group_id,
            first_club = first_club,
            second_club = second_club,
            start_time = start_time_fight 
        )

        
        user_sender = UserSender(match_id=match_data.match_id)
        match_ = Match(
            match_data = match_data,
            start_time = start_time_fight,
        )
        ClubMatchManager.add_match(match_data)
        self.scheduler_league.add_job(user_sender.send_messages_to_users, 
                                      trigger=DateTrigger(start_time_sender),
                                      misfire_grace_time = 10,
                                      
                                      )
        self.scheduler_league.add_job(match_.start_match, 
                                      trigger=DateTrigger(start_time_fight),
                                      misfire_grace_time = 10
                                      )
            
            
    async def schedule_match_start(self, match: LeagueFight):
        match_date = match.time_to_start
        
        start_time_fight = datetime.combine(match_date, datetime.min.time()).replace(hour=21, minute=0)
        start_time_sender = datetime.combine(match_date, datetime.min.time()).replace(hour=20, minute=15)
        
        
        if start_time_fight < datetime.now():
            return
        
        first_club = MatchClub(
            club_id = match.first_club.id
        )
        second_club = MatchClub(
            club_id = match.second_club.id
        )
        
        match_data = MatchData(
            match_id = match.match_id,
            group_id = match.group_id,
            first_club = first_club,
            second_club = second_club,
            start_time = start_time_fight 
        )

        
        user_sender = UserSender(match_id=match_data.match_id)
        match_ = Match(
            match_data = match_data,
            start_time = start_time_fight,
        )
        
        ClubMatchManager.add_match(match_data)
        user_sender = UserSender(match_id=match_data.match_id)
        self.scheduler_league.add_job(user_sender.send_messages_to_users,
                                      trigger=DateTrigger(start_time_sender),
                                      misfire_grace_time = 10,

                                      )
        # Напоминания о регистрации T-40 / T-15 / T-5 (Max 26.07).
        schedule_match_reminders(
            self.scheduler_league, user_sender, start_time_fight,
            blast_at=start_time_sender,
        )
        self.scheduler_league.add_job(match_.start_match,
                                      trigger=DateTrigger(start_time_fight),
                                      misfire_grace_time = 10
                                      )

class SchedulerDefaultLeague:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def start_scheduler(self):
        self.scheduler.add_job(
            func=StartDefaultLeague().setup_matches,
            trigger=CronTrigger(day=START_DAY_DEFAULT_LEAGUE, hour=8, minute=0),
            misfire_grace_time=10
        )
        self.scheduler.start()
