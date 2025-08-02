import random
from dataclasses import dataclass, field
from typing import Optional, Tuple

from database.models.blitz_character import BlitzCharacter
from database.models.blitz_team import BlitzTeam
from database.models.character import Character
from .utils import (
    calculate_bonus_donate_energy
)
from ..services.blitz_character_service import BlitzCharacterService
from ..services.blitz_team_service import BlitzTeamService


@dataclass
class MatchTeamBlitz:
    
    team_id: int
    goals: int = 0
    
    epiіsode_donate_energy: int = 0
    
    team: Optional[BlitzTeam] = None
    characters_in_match: set[Character] = field(default_factory=set)

    text_is_send_epizode_donate_energy: bool = False
    
    async def init_data(self):
        self.team: BlitzTeam = await BlitzTeamService.get_by_id(team_id=self.team_id)
        blitzs_characters: list[BlitzCharacter] = self.team.characters
        for blitz_character in blitzs_characters:
            character = await BlitzCharacterService.get_character_from_blitz_character(blitz_character)
            self.characters_in_match.add(character)

    
    @property
    def team_power(self) -> int:
        return sum(
            [
                character.full_power 
                for character in self.characters_in_match
            ]
        )
        
    @property
    def team_name(self) -> str:
        if not self.team:
            return "Team Unknown"
        return self.team.name
    
    @property
    def charactets_match_ids(self) -> list[int]:
        return [
            character.id 
            for character in self.characters_in_match
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
    
    def is_character_in_team(self, character: Character) -> bool:
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
class BlitzMatchData:
    
    match_id: str
    
    first_team: MatchTeamBlitz
    second_team: MatchTeamBlitz
    
    @property
    def first_team_id(self) -> int:
        return self.first_team.team_id
    
    @property
    def second_team_id(self) -> int:
        return self.second_team.team_id
    
    async def init_teams(self) -> None:
        await self.first_team.init_data()
        await self.second_team.init_data()

    @property
    def all_teams(self) -> list[MatchTeamBlitz]:
        return [
            self.first_team,
            self.second_team
        ]
        
    @property
    def all_characters(self) -> list[Character]:
        return [
            character for team in self.all_teams 
            for character in team.characters_in_match
        ]
    
    @property
    def all_characters_user_ids_in_match(self) -> list[int]:
        return [
            character.characters_user_id 
            for team in self.all_teams 
            for character in team.characters_in_match
        ]
    

    async def all_characters_in_teams(self) -> list[Character]:
        return [ # CH
            (await BlitzCharacterService.get_character_from_blitz_character(character)) # CH
            for team in self.all_teams # CH
            if team.team and team.team.characters # CH
            for character in team.team.characters # CH
        ]
    
    def get_chance_teams(self) -> Tuple[int, int]:
        """
        Get the chance of teams to score a goal.
        :return: Tuple of chances for the first and second teams
        """
        first_team_chance = self.power_first_team / self.total_power
        second_team_chance = self.power_second_team / self.total_power

        first_team_chance = round(first_team_chance, 6)
        second_team_chance = round(second_team_chance, 6)

        return first_team_chance, second_team_chance

    
    def get_goal_team(self) -> MatchTeamBlitz:
        values = [
            self.power_first_team, 
            self.power_second_team
        ]
        return random.choices(self.all_teams, weights=values, k=1)[0]

    def get_opposite_team(self, team_id: int) -> MatchTeamBlitz:

        return (
            self.second_team 
            if team_id == self.first_team.team_id 
            else self.first_team
        )
    
    def get_winner_team(self) -> Optional[MatchTeamBlitz]:
        """
        Get the winner team of the match.
        :return: The winner team
        """
        if self.first_team.goals > self.second_team.goals:
            return self.first_team
        elif self.second_team.goals > self.first_team.goals:
            return self.second_team
        return None
    
    @property
    def power_first_team(self) -> int:
        base_power = self.first_team.team_power
        donate_energy_bonus = calculate_bonus_donate_energy(
            donate_energy = self.first_team.epiіsode_donate_energy,
            power_club = self.first_team.team_power,
            power_opponent_club = self.second_team.team_power,
        )
        power = (
            base_power + 
            donate_energy_bonus
        )
        return power
        
    @property
    def power_second_team(self) -> int:
        base_power = self.second_team.team_power
        donate_energy_bonus = calculate_bonus_donate_energy(
            donate_energy = self.second_team.epiіsode_donate_energy,
            power_club = self.second_team.team_power,
            power_opponent_club = self.first_team.team_power,
        )
        power = (
            base_power + 
            donate_energy_bonus
        )
        return power
    
    @property
    def total_power(self) -> int:
        return self.power_first_team + self.power_second_team
