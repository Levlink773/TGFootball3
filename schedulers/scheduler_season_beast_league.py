from itertools import chain

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from constants import END_DAY_BEST_LEAGUE

from best_club_league.types import LeagueRanking

from database.models.character import Character
from database.models.league_fight import LeagueFight
from database.models.club import Club

from services.club_service import ClubService
from services.league_services.best_league_service import BestLeagueService

from collections import defaultdict
from logging_config import logger
from loader import bot

from typing import List, Tuple

class SchedulerSesonBeastLeague:

    winners_count = 10
    trigger = CronTrigger(day=END_DAY_BEST_LEAGUE, hour=12, minute=0)

    
    place_emojis = {
        1: "🥇", 
        2: "🥈", 
        3: "🥉", 
        4: "4️⃣",  
        5: "5️⃣",  
        6: "6️⃣",  
        7: "7️⃣",  
        8: "8️⃣"   
    }
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def group_matches_by_league(self, matches: list[LeagueFight]):
        grouped_matches = {ranking: [] for ranking in LeagueRanking}
        for match in matches:
            for ranking in LeagueRanking:
                if match.group_id == ranking.value:  # Сравнение с value Enum
                    grouped_matches[ranking].append(match)
        return grouped_matches

    def calculate_club_rankings(self, matches: list[LeagueFight]):
        club_points = defaultdict(int)
        for match in matches:
            club_points[match.first_club_id] += match.total_points_first_club
            club_points[match.second_club_id] += match.total_points_second_club
        return sorted(club_points.items(), key=lambda x: x[1], reverse=True)

    def calculate_league_rankings(self, matches: list[LeagueFight]):
        
        grouped_matches = self.group_matches_by_league(matches)
        league_rankings = {}
        for league, matches in grouped_matches.items():
            league_rankings[league.value] = self.calculate_club_rankings(matches)
        
        return league_rankings
            
    async def send_congratulations_group_clubs(
        self, 
        group_league: set[int, int],
        league_name: str
    ):
        text = f"🎉 Вітаємо учасників ліги {league_name}! \n\n<b>Результати</b>🔽\n\n"
        
        club_ids = [club_id for club_id, _ in group_league]
        clubs: list[Club] = await ClubService.get_clubs_by_ids(club_ids) 
        club_map = {club.id : club for club in clubs}
        for index, (club_id, count_points) in enumerate(group_league, start=1):
            club = club_map.get(club_id)
            if not club:
                continue
            place_emoji = self.place_emojis.get(index, f"{index}️⃣")
            text += f"{place_emoji} <b>{index}-е місце</b>: {club.name_club} з <code>{count_points}</code> очками.\n"

        
        characters_league = [club.characters for club in clubs]
        characters_league = list(chain(*characters_league))
        for character in characters_league:
            await self._send_massage_to_character(
                character,
                text
            )
        
    async def _send_massage_to_character(self, character: Character, text: str):
        try:
            if character.is_bot:
                return
            
            await bot.send_message(
                chat_id = character.characters_user_id,
                text = text
            )
        except Exception as E:
            logger.error(f"{E} send text {character.character_name}")
    
    async def end_season_beast_league(self):
        logger.info("ОКАНЧИВАЮ СЕЗОН ЛИГИ МАТЧЕЙ")
        matches = await BestLeagueService.get_month_league()
        group_info = self.calculate_league_rankings(matches)
        for league_name, group_league in group_info.items():
            await self.send_congratulations_group_clubs(
                group_league, 
                league_name
            )
            
    async def wait_to_end_season_best_league(self):
        self.scheduler.add_job(
            self.end_season_beast_league, 
            self.trigger,
            misfire_grace_time = 10
        )
        
        self.scheduler.start()
    