from dataclasses import dataclass, field

from database.models.character import Character
from database.models.match_character import MatchCharacter
from database.models.club_infrastructure import ClubInfrastructure

from bot.club_infrastructure.utils import calculate_bonus_by_infrastructure
from bot.club_infrastructure.types import InfrastructureType

from services.club_service import ClubService
from services.character_service import CharacterService

from services.club_infrastructure_service import ClubInfrastructureService

from utils.randomaizer import check_chance

from constants import KOEF_ENERGY_DONATE

from typing import Optional


@dataclass
class ClubsInMatch:
    first_club_id: int
    second_club_id: int
    match_id: str
    group_id: str
    
    first_club_characters: list[Character] = field(default_factory=list)
    second_club_characters: list[Character] = field(default_factory=list)
    
    goals_first_club: int = 0
    goals_second_club: int = 0

    donate_energy_first_club: int = 0
    donate_energy_second_club: int = 0

    epizode_energy_first_club: int = 0 
    epizode_energy_second_club: int = 0
    

    how_to_increment_goal: Optional[Character]  = None
    how_to_pass_goal: Optional[Character]  = None

    async def init_clubs(self):
        self.first_club  = await ClubService.get_club(club_id=self.first_club_id)
        self.second_club = await ClubService.get_club(club_id=self.second_club_id)
        
        self.first_club_infrastructure: ClubInfrastructure  = await ClubInfrastructureService.get_infrastructure(
            club_id=self.first_club_id
        )
        self.second_club_infrastructure: ClubInfrastructure = await ClubInfrastructureService.get_infrastructure(
            club_id=self.second_club_id
        )
        
        await self.add_characters_in_match()


    async def add_characters_in_match(self):
        from services.match_character_service import MatchCharacterService

        characters_in_match = await MatchCharacterService.get_characters_from_match(
            match_id=self.match_id
        )
        await self.__add_character_in_match(characters_in_match)
        if self.first_club.is_fake_club:
            characater_bot = await CharacterService.get_character_by_id(character_id=self.first_club.characters[0].id)
            result = await MatchCharacterService.add_character_in_match(club_in_match=self, character=characater_bot)
            if result:
                self.first_club_characters.append(characater_bot)
            
        if self.second_club.is_fake_club:
            characater_bot = await CharacterService.get_character_by_id(character_id=self.second_club.characters[0].id)
            result = await MatchCharacterService.add_character_in_match(club_in_match=self, character=characater_bot)
            if result:
                self.second_club_characters.append(characater_bot)
            
    
    async def __add_character_in_match(self, characters: list[MatchCharacter]):
        for character_match in characters:
            character = await CharacterService.get_character_by_id(character_id=character_match.character_id)
            if character.club_id == self.first_club_id:
                self.first_club_characters.append(character)
            elif character.club_id == self.second_club_id:
                self.second_club_characters.append(character)



    def determine_winner_users(self) -> list[Character]:
        if self.goals_first_club > self.goals_second_club:
            return self.first_club_characters
        elif self.goals_second_club > self.goals_first_club:
            return self.second_club_characters
        else:
            return self.second_club_characters + self.first_club_characters


    @property
    def clubs_is_have_no_characters(self) -> bool:
        return not self.first_club_characters and not self.second_club_characters

    @staticmethod
    def percentage_club_stength_increase(count_characters_in_club: int) -> int:
        if 0 <= count_characters_in_club <= 2:
            return 0
        elif 5 <= count_characters_in_club <= 6:
            return 5
        elif 7 <= count_characters_in_club <= 9:
            return 7
        elif 10 <= count_characters_in_club <= 11:
            return 10
        return 0

    @property
    def first_club_power(self) -> float:
        all_power = sum([character.full_power for character in self.first_club_characters]) + (self.donate_energy_first_club//KOEF_ENERGY_DONATE)
        koef_power_len_character = all_power * (self.percentage_club_stength_increase(len(self.first_club_characters))/100)
        power = all_power + koef_power_len_character + self.epizode_energy_first_club 
        power = calculate_bonus_by_infrastructure(
            self.first_club_infrastructure,
            InfrastructureType.ACADEMY_TALENT,
            power
        )
        return power[0]

    @property
    def second_club_power(self) -> float:
        all_power = sum([character.full_power for character in self.second_club_characters]) + self.donate_energy_second_club//KOEF_ENERGY_DONATE
        koef_power_len_character = all_power * (self.percentage_club_stength_increase(len(self.second_club_characters))/100)
        
        power = all_power + koef_power_len_character + self.epizode_energy_second_club 
        power = calculate_bonus_by_infrastructure(
            self.second_club_infrastructure,
            InfrastructureType.ACADEMY_TALENT,
            power
        )
        return power[0]


    @property
    def calculate_chances(self):
        total_power = self.first_club_power + self.second_club_power
        return (self.first_club_power / total_power) * 100
  
    @property
    def all_characters_in_clubs(self) -> list[Character]:
        return self.first_club.characters + self.second_club.characters
    
    @property
    def all_characters_in_match(self) -> list[Character]:
        return self.first_club_characters + self.second_club_characters
    
    @property
    def charactets_id_first_club(self) -> list[int]:
        return [character.id for character in self.first_club_characters]
    
    @property
    def charactets_id_second_club(self) -> list[int]:
        return [character.id for character in self.second_club_characters]
    
    def check_chance_win(self):
        return check_chance(self.calculate_chances)