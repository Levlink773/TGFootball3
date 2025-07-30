from match.entities import MatchClub
from typing import Tuple, Optional

from bot.club_infrastructure.types import InfrastructureType
from constants import GET_RANDOM_NUMBER

from bot.club_infrastructure.utils import calculate_bonus_by_infrastructure

from database.models.club_infrastructure import ClubInfrastructure
from database.models.character import Character

from match.message_sender.match_sender import MatchSender

from services.club_infrastructure_service import ClubInfrastructureService
from services.character_service import CharacterService

MIN_EXP = 2
MAX_EXP = 8

MIN_MONEY = 1 
MAX_MONEY = 10


class CalculateRewardMatch:
    TYPE_INFRASTRUCTURE = InfrastructureType.TRAINING_CENTER

    def __init__(
        self,
        club: MatchClub,
        sender_match: MatchSender
    ) -> None:
        
        self.club = club
        self.sender_match = sender_match
        
        self.club_infrastructure: ClubInfrastructure = None
        self.bonus_multiplier = 1
        
    @property
    def get_exp(self) -> int:
        return GET_RANDOM_NUMBER(MIN_EXP, MAX_EXP)
    
    @property
    def get_money(self) -> int:
        return GET_RANDOM_NUMBER(MIN_MONEY, MAX_MONEY)
            
    async def calculate_award_match(self) -> Tuple[int, int]:
        self.club_infrastructure = await ClubInfrastructureService.get_infrastructure(
            club_id=self.club.club_id
        )
        
        for character in self.club.characters_in_match:
            exp, money = await self._destributive_reward(character)
            await self.sender_match.send_character_reward(
                character=character,
                exp=exp,
                money=money
            )

    async def _destributive_reward(
        self, 
        character: Character,
    ):
        exp, money = calculate_bonus_by_infrastructure(
            self.club_infrastructure,
            self.TYPE_INFRASTRUCTURE,
            self.get_exp, 
            self.get_money
        )
        await CharacterService.add_exp_character(
            character_id=character.id,
            amount_exp_add=exp
        )
        await CharacterService.update_money_character(
            character_id=character.id,
            amount_money_adjustment=money
        )
        return exp, money    

    
    