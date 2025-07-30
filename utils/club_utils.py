import random
from typing import Optional

from aiogram.types import FSInputFile, Message

from database.models.character import Character
from database.models.club import Club

from services.character_service import CharacterService
from services.club_service import ClubService
from config import PositionCharacter

from utils.club_shemas import SchemaClub


from datetime import datetime, timedelta
from logging_config import logger
from loader import bot


text_schemas = {
        "sсhema_1" : "Перша схема",
        "sсhema_2" : "Друга схема",
        "sсhema_3": "Третя схема",
        "sсhema_4": "Четверта схема",
        "sсhema_5": "П'ята схема",
        "sсhema_6": "Шоста схема"
    }

async def get_club_text(club: Club, character: Character) -> str:
    character_leader = await CharacterService.get_character(character_user_id=club.owner.user_id)
    text_leader = (
        f"{character_leader.character_name}"
        f"[{character_leader.owner.link_to_user}]"
        f"[💪 <b>{character_leader.full_power:.2f}</b>]"
        f"[<b>{character_leader.level} рів.</b>]"
        f"[<b>{character_leader.acronym_position}</b>]"
    )
    club = await ClubService.get_club(club_id=club.id)
    
    text = f"""
⚽ Гравець: {character.character_name}

🏆 Команда: {club.name_club}
👑 Лідер: {text_leader}
🏅 Дивізіон: {club.league}
📝 Опис команди: {club.description}

📊 Моє місце в рейтингу команді: {calculate_character_rank(
        my_character=character,
        characters_list=club.characters
    )}

💪 Загальна сила команди: {club.total_power:.2f}
👥 Кількість членів у команді: {len(club.characters)}
    """
    if club.link_to_chat:
        text += f'\n💬 Чат команди: <a href="{club.link_to_chat}">Чат</a>'
    
    return text


async def get_club_description(club: Club) -> str:
    character_leader = await CharacterService.get_character(character_user_id=club.owner.user_id)
    text_leader = f"{character_leader.character_name} [{character_leader.owner.link_to_user}] [💪 <b>{character_leader.full_power:.2f}</b>] [<b>{character_leader.level} рів.</b>][<b>{character_leader.acronym_position}</b>]"
    club = await ClubService.get_club(club_id=club.id)
    text_invite = "<b>вільний</b> — приєднуйся без запрошення!"
    if club.is_invite_only:
        text_invite = "<b>лише за запрошенням</b> — подай запит, щоб стати частиною еліти 🧐"
    
    text = f"""
⚽ Команда: {club.name_club}

👑 Лідер: {text_leader}
🏅 Дивізіон: {club.league}
💪 Загальна сила команди: {club.total_power:.2f}
👥 Кількість членів у команді: {len(club.characters)}

🛂 Вступ до команди: {text_invite}

🏢 Опис: <i>{club.description}</i>
    """
    return text


def calculate_character_rank(my_character: Character, characters_list: list[Character]) -> int:
    sorted_characters = sorted(characters_list, key=lambda character: character.full_power, reverse=True)
    for index, character in enumerate(sorted_characters, start=1):
        if character.id == my_character.id:
            return index
        

def get_text_education_center_reward(exp: int, coins: int, energy: int, delta_time_education_reward: timedelta) -> str:
    current_time = datetime.now()
    next_reward_time = current_time + delta_time_education_reward
    next_reward_time_formatted = next_reward_time.strftime("%d-%m-%Y %H:%M:%S")
    
    
    message = f"""
🎓 <b>Після навчального центру ваш персонаж отримав:</b>
✨ {exp} <b>досвіду</b>  
💰 {coins} <b>монет</b>
🔋 {energy} <b>енергії</b>

🕒 <b>Ви зможете отримати наступну нагороду через:</b> {delta_time_education_reward} <b>о {next_reward_time_formatted}</b>
"""
    return message


def rating_club(club: Club, character: Character) -> str:
    def get_medal_emoji(rank: int) -> str:
        if rank == 1:
            return "🥇"
        elif rank == 2:
            return "🥈"
        elif rank == 3:
            return "🥉"
        else:
            return "🏅"

    sorted_characters = sorted(club.characters, key=lambda c: c.full_power, reverse=True)
    rank_texts = []
    
    for idx, char in enumerate(sorted_characters, start=1):
        medal = get_medal_emoji(idx)
        if char.characters_user_id == character.characters_user_id:
            rank_texts.append(
                f"{medal} {idx} місце - <b><a href='tg://user?id={char.characters_user_id}'>{char.character_name}</a>🩳 </b> "
                f"[💪 <b>{char.full_power:.2f}</b>] [<b>{char.level} рів.</b>]"
                f"[<b>{char.acronym_position}</b>]"
            )
        else:
            rank_texts.append(
                f"{medal} {idx} місце - <a href='tg://user?id={char.characters_user_id}'>{char.character_name}</a> "
                f"[<b>💪 {char.full_power:.2f}</b>] [<b>{char.level} рів.</b>]"
                f"[<b>{char.acronym_position}</b>]"

            )
    
    ranking_text = "\n".join(rank_texts)
    return ranking_text

def get_text_schemas(club: Club):

    
    text = """
Поточна схема: {my_schema}
    
⚽ Схема команди на матч ⚽
Ваша команда готова до бою! Ось як розподіляються гравці на полі для майбутнього матчу:

🧤 Воротар [GK]: {goalkeeper} гравець - він не пропустить жодного м'яча! Це останній рубіж оборони, який охороняє ворота.

🛡 Захисники [DF]: {defenders} гравця - ваші герої оборони! Вони стоять стіною перед воротами, захищаючи команду від атак суперника.

⚡ Нападники [FW]: {attackers} гравця - це ваші найкращі голеадори! Вони завжди готові завдати вирішального удару і забити гол.

🎯 Півзахисники [MF]: {midfielder} гравця - головні майстри поля! Вони керують грою, роздають передачі і допомагають як у захисті, так і в атаці.
    """
    
    current_chema = SchemaClub.__getattribute__(SchemaClub, club.schema)
    return text.format(
        my_schema  = text_schemas[club.schema],
        defenders  = current_chema[PositionCharacter.DEFENDER],
        midfielder = current_chema[PositionCharacter.MIDFIELDER],
        attackers  = current_chema[PositionCharacter.ATTACKER],
        goalkeeper = current_chema[PositionCharacter.GOALKEEPER]
    )


async def send_message_characters_club(
    characters_club: list[Character],                                   
    my_character: Character | None, 
    text: str,
    photo: Optional[str | FSInputFile] = None
) -> Optional[Message]:
        
    messages_photos = []
    for character in characters_club:
        if my_character and character.characters_user_id == my_character.characters_user_id:
            continue
        try:
            if photo:
                message_photo = await bot.send_photo(
                    chat_id=character.characters_user_id,
                    photo=photo,
                    caption=text
                )
                messages_photos.append(message_photo)
            else:
                await bot.send_message(chat_id= character.characters_user_id, text = text)
                
        except Exception as E:
            logger.error(f"НЕ СМОГ ОТПРАВИТЬ СООБЩЕНИЕ ПЕРСОНАЖУ {character.character_name}")
    
    return random.choice(messages_photos) if messages_photos else []
            
            