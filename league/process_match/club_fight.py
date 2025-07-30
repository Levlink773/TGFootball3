import asyncio
import random

from asyncio import Queue

from datetime import datetime

from bot.club_infrastructure.config import INFRASTRUCTURE_BONUSES
from bot.club_infrastructure.types import InfrastructureType
from constants import TIME_FIGHT, BUFFER_TIME, GET_RANDOM_NUMBER, PositionCharacter

from database.models.character import Character
from database.models.club_infrastructure import ClubInfrastructure

from services.character_service import CharacterService
from services.club_infrastructure_service import ClubInfrastructureService
from services.league_service import LeagueFightService
from services.match_character_service import MatchCharacterService

from .club_in_match import ClubsInMatch
from .fight_sender_v2 import ClubMatchSender


# from logging_config import logger

# class ClubMatchManager:
#     all_fights: dict[str, "ClubMatch"] = {}
    
#     @classmethod
#     def register_fight(cls, fight: 'ClubMatch'):
#         cls.all_fights[fight.clubs_in_match.match_id] = fight

#     @classmethod
#     def get_fight_by_id(cls, match_id: str) -> 'ClubMatch':
#         return cls.all_fights.get(match_id)

#     @classmethod
#     def get_match_by_club(cls, club_id: int) -> list['ClubMatch']:
#         return [fight for fight in cls.all_fights.values() 
#                 if fight.clubs_in_match.first_club_id == club_id 
#                     or 
#                 fight.clubs_in_match.second_club_id == club_id]


# class ClubMatch:
#     def __init__(self, first_club_id: int, 
#                  second_club_id: int,
#                  start_time:datetime,
#                  match_id: str,
#                  group_id: str
#                  ):
        
#         self.start_time  = start_time
#         self.group_id    = group_id
#         self.total_goals = random.choice(range(4,9))
        
#         self.clubs_in_match = ClubsInMatch(
#             first_club_id  = first_club_id,
#             second_club_id = second_club_id,
#             match_id = match_id,
#             group_id=group_id
#         )
        
#         self.first_club_id  = first_club_id
#         self.second_club_id = second_club_id
        
#         self.club_match_sender = ClubMatchSender(self.clubs_in_match)
#         self._queue_timer = Queue()
#         ClubMatchManager.register_fight(self)

#     async def start_match(self):
#         await self.clubs_in_match.init_clubs()
#         if self.clubs_in_match.clubs_is_have_no_characters:
#             return await self.club_match_sender.send_no_participants()
        
#         await asyncio.sleep(0.01)
#         await self.club_match_sender.send_start_match()
#         await self.club_match_sender.send_participants_characters()
        
#         await self.starting_taimer_match()
#         await self.winners_remuneration()
#         await self.club_match_sender.send_end_match()
    
#     async def add_goal_to_character(self, character_in_club: list[Character]):
#         if len(character_in_club) > 1:
#             eligible_characters = [
#                 character for character in character_in_club
#                 if character.position_enum != PositionCharacter.GOALKEEPER
#             ]
#         else:
#             eligible_characters = character_in_club

#         power_chance_characters = [character.full_power for character in eligible_characters]
#         character_score_goal = random.choices(eligible_characters, weights=power_chance_characters, k=1)[0]
#         self.clubs_in_match.how_to_increment_goal = character_score_goal
#         self.clubs_in_match.how_to_pass_goal = random.choice(
#             [character for character in character_in_club if character.id != character_score_goal.id]
#         ) if len(character_in_club) > 1 else None
#         await MatchCharacterService.add_goal_to_character(match_id=self.clubs_in_match.match_id, character_id=character_score_goal.id)
                    
                    
#     async def _update_score(self) -> list[Character]:
#         if self.clubs_in_match.check_chance_win():
#             club_id = self.clubs_in_match.first_club_id
#             self.clubs_in_match.goals_first_club += 1
#             chatacters_club = self.clubs_in_match.first_club_characters
#         else:
#             club_id = self.clubs_in_match.second_club_id
#             self.clubs_in_match.goals_second_club += 1
#             chatacters_club = self.clubs_in_match.second_club_characters
            
#         await LeagueFightService.increment_goal(
#             match_id=self.clubs_in_match.match_id,
#             club_id=club_id
#             )
#         self.clubs_in_match.epizode_energy_first_club = 0
#         self.clubs_in_match.epizode_energy_second_club = 0
#         return chatacters_club, club_id
    
    
#     #TAIMERS
#     async def starting_taimer_match(self):
#         start_time_taimer = datetime.now()
#         asyncio.create_task(self._timer_event_generate(start_time_taimer))
#         await self._timer_event_match(start_time_taimer)
        
#     def generate_goal_times(self, start_timestamp: int, total_goals: int, end_timestamp: int) -> list[int]:
#         min_gap = 45
#         start_timestamp = start_timestamp+min_gap
#         match_duration = end_timestamp - start_timestamp
#         first_half_end = start_timestamp + match_duration // 2
        
#         first_half_goals = total_goals // 2
#         second_half_goals = total_goals - first_half_goals

#         def generate_times(start, end, goals, gap):
#             interval = (end - start) // goals
#             times = []
#             last_time = start

#             for _ in range(goals):
#                 next_time = last_time + gap + random.randint(0, max(0, interval - gap))
#                 if next_time > end:
#                     break
#                 times.append(next_time)
#                 last_time = next_time
#             return times

#         first_half_times = generate_times(start_timestamp, first_half_end, first_half_goals, min_gap)
#         second_half_times = generate_times(first_half_end, end_timestamp, second_half_goals, min_gap) 

#         goal_times = sorted(first_half_times + second_half_times)
#         return goal_times
                
#     async def _timer_event_generate(self, match_time_start: datetime):
#         match_time_end = match_time_start + TIME_FIGHT
#         start_timestamp = int(match_time_start.timestamp())
#         end_timestamp = int(match_time_end.timestamp())
        
#         goal_times = self.generate_goal_times(
#             start_timestamp=start_timestamp,
#             total_goals=self.total_goals,
#             end_timestamp = end_timestamp
#         )
#         for goal_time in goal_times:
#             current_time = datetime.now()
#             sleep_time = goal_time - current_time.timestamp() - 40 
            
#             if sleep_time > 0:
#                 await asyncio.sleep(sleep_time) 
#                 await self.club_match_sender.send_coming_goal(goal_time)
            

#             remaining_time = goal_time - datetime.now().timestamp()
#             if remaining_time > 0:
#                 await asyncio.sleep(remaining_time)
            

#             club_characters_score_goal, club_id_goal = await self._update_score()
#             await self.add_goal_to_character(club_characters_score_goal)
#             await self._queue_timer.put(club_id_goal)
        
#         await asyncio.sleep(BUFFER_TIME.total_seconds())


#     async def halfway_notification(self):
#         await asyncio.sleep((TIME_FIGHT / 2).total_seconds())
#         await self.club_match_sender.send_end_time()
    
#     async def _timer_event_match(self, match_time_start: datetime):
#         match_time_end = match_time_start + TIME_FIGHT
#         asyncio.create_task(self.halfway_notification())
        
#         CHECK_INTERVAL = TIME_FIGHT // 9
        
#         while True:
#                 current_time = datetime.now()
#                 if current_time.replace(second=0, microsecond=0) >= match_time_end.replace(second=0, microsecond=0):
#                     break
#                 timeout = min(CHECK_INTERVAL, match_time_end - current_time).total_seconds()
#                 try:
#                     club_id_goal = await asyncio.wait_for(self._queue_timer.get(), timeout=timeout)
#                     await self.sender_info_goals("goal", club_id_goal)
#                 except asyncio.TimeoutError:
#                     await self.sender_info_goals("no_goal")
#                 except Exception as E:
#                     print(E)
        
        
#     async def sender_info_goals(self, type_event: str, club_id_goal: int|None = None) -> None:
        
#         async def send_goal_event(goal_type:str, characters: list[Character]):
#             await self.club_match_sender.send_goal_event(
#                 characters = characters,
#                 goal_event = goal_type,
#             )
        
#         if type_event == "goal":
#             characters_goal_conceded = self.clubs_in_match.first_club_characters if club_id_goal == self.first_club_id else self.clubs_in_match.second_club_characters 
#             characters_goal_increment = self.clubs_in_match.first_club_characters if club_id_goal != self.first_club_id else self.clubs_in_match.second_club_characters 
#             await send_goal_event("goal", characters_goal_conceded)
#             await send_goal_event("goal_conceded", characters_goal_increment)
#         else:
#             await send_goal_event("no_goal", self.clubs_in_match.all_characters_in_match)
        
#     async def winners_remuneration(self):
        
#         winners_characters = self.clubs_in_match.determine_winner_users()    
#         for winner_character in winners_characters:
#             if not winner_character.is_bot:
                
#                 exp, coins = await self.calculation_bonus(winner_character)
                
#                 await CharacterService.add_exp_character(
#                     character_id=winner_character.id,
#                     amount_exp_add=exp
#                 )
#                 await CharacterService.update_money_character(
#                     character_id=winner_character.id,
#                     amount_money_adjustment=coins
#                 )
#                 await self.club_match_sender.send_reward(
#                     character = winner_character,
#                     exp = exp,
#                     money = coins 
#                 )
                
#     async def calculation_bonus(self, character: Character) -> tuple[int, int]:
#         TYPE_INFRASTRUCTURE = InfrastructureType.TRAINING_CENTER
#         exp   = GET_RANDOM_NUMBER()
#         coins = GET_RANDOM_NUMBER()

#         bonus_multiplier = 1
#         if character.club:
#             infrastructure: ClubInfrastructure = await ClubInfrastructureService.get_infrastructure(
#                 club_id=character.club_id
#             )
#             bonus_multiplier += (
#                 INFRASTRUCTURE_BONUSES[TYPE_INFRASTRUCTURE].get(
#                 infrastructure.get_infrastructure_level(TYPE_INFRASTRUCTURE))
#                 ) / 100
            
#         exp, coins = apply_multiplier((exp, coins), bonus_multiplier)

#         return int(exp), int(coins)


# def apply_multiplier(rewards: tuple[int, int], multiplier: int) -> tuple[int, int]:
#     return tuple(value * multiplier for value in rewards)