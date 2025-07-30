from database.models.character import Character

async def get_new_member_characters(characters: list[Character]) -> str:
    text = f"Последние {len(characters)} зарегистрированных персонажей\n\n"
    
    for index, character in enumerate(characters, start=1):
        text_club = character.club.name_club if character.club_id else "Не в команде"
        text += (
            f"{index}." 
            f"Ник - [{character.character_name}][{character.owner.link_to_user}]\n"
            f"Команда - {text_club}]\n"
            f"Дата регистрации - {character.created_at}\n\n"
            
        )
       
        
    return text