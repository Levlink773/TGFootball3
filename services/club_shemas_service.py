from utils.club_shemas import SchemaClub

from database.models.character import Character
from database.models.club import Club

from services.match_character_service import MatchCharacterService
from services.character_service import CharacterService


class SchemaSerivce(SchemaClub):
    
    @classmethod
    async def character_is_enough_room(
        cls, 
        club: Club, 
        match_id: str, 
        my_character: Character
    ) -> bool:
        
        characters_in_match = await MatchCharacterService.get_charaters_club_in_match(
            match_id=match_id,
            club_id=club.id
        )

        characters:list[Character] = []
        for character_match in characters_in_match:
            character = await CharacterService.get_character_by_id(character_id=character_match.character_id)
            characters.append(character)
        
        limit_character = getattr(cls, club.schema)[my_character.position_enum]
        return sum(1 for character in characters if character.position_enum == my_character.position_enum ) < limit_character
        