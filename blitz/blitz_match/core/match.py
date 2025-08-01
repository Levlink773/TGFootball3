import random
from asyncio import Semaphore
from datetime import datetime, timedelta
from typing import Optional

from constants import TIME_FIGHT

from match.constans import TIME_EVENT_DONATE_ENERGY
from match.entities import MatchData, MatchClub
from match.enum import TypeGoalEvent
from match.message_sender.match_sender import MatchSender

from database.models.character import Character

from services.match_character_service import MatchCharacterService
from services.character_service import CharacterService
from services.league_services.league_service import LeagueService

from logging_config import logger

from .goal_generator import GoalGenerator
from .utils import CalculateRewardMatch

semaphore_add_key = Semaphore(2)

class Match:
    SCORE_POINTS_BY_EVENT = {
        TypeGoalEvent.GOAL: 1,
        TypeGoalEvent.NO_GOAL: 0.25
    }
    
    def __init__(
        self,
        match_data: MatchData,
        start_time: datetime
    ) -> None:

        self.match_data = match_data
        self.match_sender = MatchSender(match_data)        
        self.count_goals = self._generate_count_goals()
        
        end_time = start_time + TIME_FIGHT
            
            
        self.goal_generator = GoalGenerator(
            start_time  = start_time,
            end_time    = end_time,
            count_goals = self.count_goals
        )
            
    def _generate_count_goals(self) -> int:
        return random.randint(3,9)
            
    async def start_match(self) -> None:
        await self.match_data.init_clubs()
        
        if not self.match_data.clubs_have_characters():
            return await self.match_sender.send_no_characters_in_match()
        
        await self.goal_generator.start()
        await self.match_sender.start_match()
        await self.match_sender.send_participants_match()
        await self.event_watcher()
        await self.end_match()
        await self.destribute_mvp_match()
    
    async def event_watcher(self) -> None:
        event_func: dict[TypeGoalEvent, callable] = {
            TypeGoalEvent.NO_GOAL: self.no_goal_event,
            TypeGoalEvent.PING_DONATE_ENERGY: self.ping_donate_energy_event,
            TypeGoalEvent.GOAL: self.goal_event,
        }

        async for event in self.goal_generator.generate_goals():
            if event is None:
                break
            await event_func[event]()
            for club in self.match_data.all_clubs:
                club.anulate_donate_energy()

    async def no_goal_event(self) -> None:
        TYPE_EVENT = TypeGoalEvent.NO_GOAL
        
        first_character = self.match_data.first_club.get_character_by_power()
        second_character = self.match_data.second_club.get_character_by_power()
        characters_scene = [character for character in [first_character, second_character] if character]
        await self.match_sender.send_event_scene(
            goal_event = TYPE_EVENT,
            characters_scene = characters_scene
        )
        for character in [first_character, second_character]:  
            if not character:
                continue
            
            await self._add_event(
                character = character,
                score_add = 0.25
            )

           
    async def ping_donate_energy_event(self) -> None:
        goal_time = (
            datetime.now() + timedelta(seconds=TIME_EVENT_DONATE_ENERGY)
        ).timestamp()
        await self.match_sender.send_ping_donate_energy(int(goal_time))
        
        
    async def goal_event(self) -> None:
        goal_club = self.match_data.get_goal_club()
        goal_club.add_goal()
        character_goal = goal_club.get_character_by_power()
        if not character_goal:
            return
        
        assist_character = goal_club.get_character_by_power(
            no_character=character_goal
        )
        await self.match_sender.send_event_scene(
            goal_event = TypeGoalEvent.GOAL,
            character_goal = character_goal,
            goal_club = goal_club,
            character_assist = assist_character,
        )
        await self._add_event(
            character = character_goal,
            score_add = 1
        )
        await MatchCharacterService.add_goal_to_character(
            match_id = self.match_data.match_id,
            character_id = character_goal.id,
        )
        await LeagueService.increment_goal(
            match_id=self.match_data.match_id,
            club_id=goal_club.club_id
            )

        if assist_character:
            await self._add_event(
                character = assist_character,
                score_add = 0.75
            )
        
        
    async def end_match(self) -> None:
        winner_match_club = self.match_data.get_winner_club()
        await self.match_sender.send_end_match(
            winner_match_club = winner_match_club
        )
        await self.award_distribution(
            winner_match_club
        )
    async def destribute_mvp_match(self):
        first_character = None
        second_character = None
        
        mvp_first_club = await MatchCharacterService.get_match_mvp(
            match_id=self.match_data.match_id,
            club_id=self.match_data.first_club_id
        )   
        mvp_second_club = await MatchCharacterService.get_match_mvp(
            match_id=self.match_data.match_id,
            club_id=self.match_data.second_club_id
        )
        if mvp_first_club is not None:
            first_character = await CharacterService.get_character_by_id(
                character_id = mvp_first_club.character_id
            )
        if mvp_second_club is not None:
            second_character = await CharacterService.get_character_by_id(
                character_id = mvp_second_club.character_id
            )
        async with semaphore_add_key:
            for character in [first_character, second_character]:
                if not character:
                    continue

                await CharacterService.add_trainin_key(
                    character_id = character.id
                )
        
        await self.match_sender.send_congratulation_mvp(
            first_mvp=[mvp_first_club, first_character] if mvp_first_club else None,
            second_mvp=[mvp_second_club, second_character] if mvp_second_club else None
        )
        
        
    async def award_distribution(
        self, 
        winner_match_club: Optional[MatchClub],            
    ) -> None:
        
        if winner_match_club is None:
            return
        calculate_reward = CalculateRewardMatch(
            club = winner_match_club,
            sender_match = self.match_sender
        )
        
        await calculate_reward.calculate_award_match()
        
        
    async def _add_event(
        self,
        character: Character,
        score_add: int = 0.25
    ) -> None:
        await MatchCharacterService.add_score_to_character(
            character_id = character.id,
            match_id = self.match_data.match_id,
            add_score = score_add
        )