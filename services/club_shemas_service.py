from utils.club_shemas import SchemaClub

from database.models.character import Character
from database.models.club import Club

from services.match_character_service import MatchCharacterService
from services.character_service import CharacterService

from logging_config import logger


class SchemaSerivce(SchemaClub):

    # club.schema is a free String(255) written from bot callback data. Any value
    # that is not a real formation makes getattr() below return a method (or raise),
    # breaking match registration for EVERY member of that club.
    # Derived, never retyped: the names contain a Cyrillic 'с' (U+0441).
    _VALID_SCHEMAS = {k for k, v in vars(SchemaClub).items() if isinstance(v, dict)}
    _DEFAULT_SCHEMA = Club.__table__.c.schema.default.arg

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
        
        schema_name = club.schema if club.schema in cls._VALID_SCHEMAS else cls._DEFAULT_SCHEMA
        if schema_name != club.schema:
            logger.error(
                "club %s has invalid schema %r; falling back to %s",
                club.id, club.schema, schema_name,
            )
        limit_character = getattr(cls, schema_name)[my_character.position_enum]
        return sum(1 for character in characters if character.position_enum == my_character.position_enum ) < limit_character
        