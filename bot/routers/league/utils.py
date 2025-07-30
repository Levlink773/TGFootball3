from bot.club_infrastructure.config import INFRASTRUCTURE_BONUSES
from bot.club_infrastructure.types import InfrastructureType

from database.models.character import Character
from database.models.match_character import MatchCharacter
from database.models.club_infrastructure import ClubInfrastructure

from services.match_character_service import MatchCharacterService
from services.character_service import CharacterService
from services.club_infrastructure_service import ClubInfrastructureService

async def get_characters_club_in_match(club_id: int, match_id: str) -> list[Character]:
    characters_in_match = []
    try:
        characters_club_in_match: list[MatchCharacter] = await MatchCharacterService.get_charaters_club_in_match(
            match_id = match_id,
            club_id  = club_id
        )
        for character_match in characters_club_in_match:
            character: Character = await CharacterService.get_character_by_id(
                character_id = character_match.character_id
            )
            characters_in_match.append(character)
    except Exception as E:
        ...
        
    finally:
        return characters_in_match
    