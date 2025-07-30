from config import PositionCharacter
 
from services.match_character_service import MatchCharacterService
from services.character_service import CharacterService

from database.models.character import Character
from database.models.club import Club

class SchemaClub:
    
    sсhema_1 = {
        PositionCharacter.DEFENDER : 4,
        PositionCharacter.MIDFIELDER : 4,
        PositionCharacter.ATTACKER : 2,
        PositionCharacter.GOALKEEPER : 1,
    }
    
    sсhema_2 = {
        PositionCharacter.DEFENDER : 4,
        PositionCharacter.MIDFIELDER : 3,
        PositionCharacter.ATTACKER : 3,
        PositionCharacter.GOALKEEPER : 1,
    }
    
    sсhema_3 = {
        PositionCharacter.DEFENDER : 3,
        PositionCharacter.MIDFIELDER : 5,
        PositionCharacter.ATTACKER : 2,
        PositionCharacter.GOALKEEPER : 1,
    }
    
    sсhema_4 = {
        PositionCharacter.DEFENDER : 3,
        PositionCharacter.MIDFIELDER : 4,
        PositionCharacter.ATTACKER : 3,
        PositionCharacter.GOALKEEPER : 1,
    }
     
    sсhema_5 = {
        PositionCharacter.DEFENDER : 5,
        PositionCharacter.MIDFIELDER : 3,
        PositionCharacter.ATTACKER : 2,
        PositionCharacter.GOALKEEPER : 1,
    }
    
    sсhema_6 = {
        PositionCharacter.DEFENDER : 4,
        PositionCharacter.MIDFIELDER : 5,
        PositionCharacter.ATTACKER : 1,
        PositionCharacter.GOALKEEPER : 1,
    }

