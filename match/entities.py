import random
from datetime import datetime
from typing import Optional, Literal, Tuple

from dataclasses import dataclass, field

from database.models.club import Club
from database.models.character import Character
from database.models.club_infrastructure import ClubInfrastructure

from bot.club_infrastructure.types import InfrastructureType
from bot.club_infrastructure.utils import (
    calculate_bonus_by_infrastructure,
)

from services.character_service import CharacterService
from services.match_character_service import MatchCharacterService
from services.club_service import ClubService
from services.club_infrastructure_service import ClubInfrastructureService

from .utils import (
    calculate_bonus_from_count_characters,
    calculate_bonus_donate_energy
)

from constants import TIME_FIGHT


@dataclass
class MatchClub:
    
    club_id: int
    goals: int = 0
    
    epiіsode_donate_energy: int = 0
    
    club: Optional[Club] = None
    characters_in_match: set[Character] = field(default_factory=set)
    
    club_infrastructure: Optional[ClubInfrastructure] = None
    text_is_send_epizode_donate_energy: bool = False
    
    async def init_data(self):
        self.club: Club = await ClubService.get_club(
            club_id=self.club_id
        )
        self.club_infrastructure = await ClubInfrastructureService.get_infrastructure(
            club_id=self.club_id
        )
    
    async def join_characters(
        self, 
        match_id: str,
        group_id: str
    ) -> None:
        if not self.club:
            return
        
        if self.club.is_fake_club:
            characater_bot = (
                await CharacterService.get_character_by_id(
                    character_id=self.club.characters[0].id
                )
            )
            result = (
                await MatchCharacterService.add_character_in_match(
                    match_id=match_id,
                    club_id=self.club.id,
                    group_id = group_id,
                    character_id = characater_bot.id
                )
            )
            if result:
                self.characters_in_match.add(characater_bot)
        
        characters_in_match = await MatchCharacterService.get_charaters_club_in_match(
            match_id=match_id,
            club_id = self.club_id
        )
        for match_character in characters_in_match:
            character = await CharacterService.get_character_by_id(
                character_id=match_character.character_id
            )
            if character.club_id != self.club_id:
                continue
            self.characters_in_match.add(character)
    
    @property
    def club_power(self) -> int:
        return sum(
            [
                character.full_power 
                for character in self.characters_in_match
            ]
        )
        
    @property
    def club_name(self) -> str:
        if not self.club:
            return "Unknown Club"
        return self.club.name_club
    
    @property
    def stadium_name(self) -> str:
        if not self.club.custom_name_stadion:
            return "Unknown Stadium"
        return self.club.custom_name_stadion
    
    @property
    def charactets_match_ids(self) -> list[int]:
        return [
            character.id 
            for character in self.characters_in_match
        ]
        
    def get_charaters_by_position(
        self, 
        position: Literal[
            "Воротар",
            "Захисник",
            "Півзахисник",
            "Нападник"
        ]
    ) ->list[Character]:
        return [
            character
            for character in self.characters_in_match
            if character.position_enum == position
        ]
    
    def get_character_by_power(
        self,
        no_character: Optional[Character] = None
    ) -> Optional[Character]:
        if not self.characters_in_match:
            return None

        filtered_characters = [
            character for character in self.characters_in_match
            if not no_character or character.characters_user_id != no_character.characters_user_id
        ]

        if not filtered_characters:
            return None

        weights = [character.full_power for character in filtered_characters]

        selected_character = random.choices(filtered_characters, weights=weights, k=1)[0]
        return selected_character
    
    def is_character_in_club(self, character: Character) -> bool:
        characters_ids = [
            character.id 
            for character in self.characters_in_match
        ]
        return character.id in characters_ids
        
    def add_goal(self) -> None:
        self.goals += 1
        
    def anulate_donate_energy(self) -> None:
        self.epiіsode_donate_energy = 0
        self.text_is_send_epizode_donate_energy = False
        
@dataclass
class MatchData:
    
    match_id: str
    group_id: str
    
    first_club: MatchClub
    second_club: MatchClub 
    
    start_time: datetime

    @property
    def end_time(self) -> datetime:
        return self.start_time + TIME_FIGHT
    
    @property
    def first_club_id(self) -> int:
        return self.first_club.club_id
    
    @property
    def second_club_id(self) -> int:
        return self.second_club.club_id
    
    async def init_clubs(self) -> None:
        await self.first_club.init_data()
        await self.second_club.init_data()
        for club in self.all_clubs:
            await club.join_characters(
                match_id=self.match_id,
                group_id=self.group_id
            )
        
        
    def clubs_have_characters(self) -> bool:
        return (
                bool(self.first_club.characters_in_match) 
            or 
                bool(self.second_club.characters_in_match)
        )
    
    @property
    def all_clubs(self) -> list[MatchClub]:
        return [
            self.first_club,
            self.second_club
        ]
        
    @property
    def all_characters(self) -> list[Character]:
        return [
            character for club in self.all_clubs 
            for character in club.characters_in_match
        ]
    
    @property
    def all_characters_user_ids_in_match(self) -> list[int]:
        return [
            character.characters_user_id 
            for club in self.all_clubs 
            for character in club.characters_in_match
        ]
    
    
    @property
    def all_characters_in_clubs(self) -> list[Character]:
        return [
            character for club in self.all_clubs 
            for character in club.club.characters
        ]
    
    def get_chance_clubs(self) -> Tuple[int, int]:
        """
        Get the chance of clubs to score a goal.
        :return: Tuple of chances for the first and second clubs
        """
        first_club_chance = self.power_first_club / self.total_power
        second_club_chance = self.power_second_club / self.total_power

        first_club_chance = round(first_club_chance, 6)
        second_club_chance = round(second_club_chance, 6)

        return first_club_chance, second_club_chance

    
    def get_goal_club(self) -> MatchClub:
        values = [
            self.power_first_club, 
            self.power_second_club
        ]
        return random.choices(self.all_clubs, weights=values, k=1)[0]

    def get_opposite_club(self, club_id: int) -> MatchClub:

        return (
            self.second_club 
            if club_id == self.first_club.club_id 
            else self.first_club
        )
    
    def get_winner_club(self) -> Optional[MatchClub]:
        """
        Get the winner club of the match.
        :return: The winner club
        """
        if self.first_club.goals > self.second_club.goals:
            return self.first_club
        elif self.second_club.goals > self.first_club.goals:
            return self.second_club
        return None
    
    @property
    def power_first_club(self) -> int:
        base_power = self.first_club.club_power
        bonus_len_characters = calculate_bonus_from_count_characters(
            len(self.first_club.characters_in_match),
            power = base_power
        )
        base_power = calculate_bonus_by_infrastructure(
            self.first_club.club_infrastructure,
            InfrastructureType.ACADEMY_TALENT,
            base_power
        )[0]
        donate_energy_bonus = calculate_bonus_donate_energy(
            donate_energy = self.first_club.epiіsode_donate_energy,
            power_club = self.first_club.club_power,
            power_opponent_club = self.second_club.club_power,
        )
        power = (
            base_power + 
            bonus_len_characters + 
            donate_energy_bonus
        )
        return power
        
    @property
    def power_second_club(self) -> int:
        base_power = self.second_club.club_power
        bonus_len_characters = calculate_bonus_from_count_characters(
            len(self.second_club.characters_in_match),
            power = base_power
        )
        base_power = calculate_bonus_by_infrastructure(
            self.second_club.club_infrastructure,
            InfrastructureType.ACADEMY_TALENT,
            base_power
        )[0]
        donate_energy_bonus = calculate_bonus_donate_energy(
            donate_energy = self.second_club.epiіsode_donate_energy,
            power_club = self.second_club.club_power,
            power_opponent_club = self.first_club.club_power,
        )
        power = (
            base_power + 
            bonus_len_characters + 
            donate_energy_bonus
        )
        return power
    
    @property
    def total_power(self) -> int:
        return self.power_first_club + self.power_second_club
