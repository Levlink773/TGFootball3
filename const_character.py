from datetime import datetime
from database.models.character import Character
from constants import PositionCharacter



def create_defender() -> Character:
    return Character(
        name="",
        position = PositionCharacter.DEFENDER,
        technique=3,
        kicks=4,
        ball_selection=7,
        speed=6,
        endurance=5,
        gender="",
        exp=0,
        money=0,
        created_at=datetime.now()
    )

def create_midfielder() -> Character:
    return Character(
        name="",
        position = PositionCharacter.MIDFIELDER,
        technique=4,
        kicks=3,
        ball_selection=8,
        speed=6,
        endurance=6,
        gender="",
        exp=0,
        money=0,
        created_at=datetime.now()
    )

def create_goalkeeper() -> Character:
    return Character(
        name="",
        position = PositionCharacter.GOALKEEPER,
        technique=2,
        kicks=5,
        ball_selection=5,
        speed=5,
        endurance=8,
        gender="",
        exp=0,
        money=0,
        created_at=datetime.now()
    )

def create_attacker() -> Character:
    return Character(
        name="",
        position = PositionCharacter.ATTACKER,
        technique=3,
        kicks=7,
        ball_selection=2,
        speed=7,
        endurance=6,
        gender="",
        exp=0,
        money=0,
        created_at=datetime.now()
    )

def CREATE_CHARACTER_CONST(position: PositionCharacter) -> Character:
    if position == PositionCharacter.DEFENDER:
        return create_defender()
    elif position == PositionCharacter.MIDFIELDER:
        return create_midfielder()
    elif position == PositionCharacter.GOALKEEPER:
        return create_goalkeeper()
    elif position == PositionCharacter.ATTACKER:
        return create_attacker()
    
    
    