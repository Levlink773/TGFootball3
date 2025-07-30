from bot.keyboards.club_keyboard import send_invite_to_join_club

from database.models.character import Character
from database.models.club import Club

from loader import bot
from constants import CHARACTER_SEND_OFFER_JOIN_TO_CLUB

TEXT_TEMPLATE_JOIN_CHARATER = """
📬 <b>Запрос на вступление в клуб</b>

👤 <b>Имя:</b> {name}
🎮 <b>Уровень:</b> {lvl} 

<blockquote>
🎯 <b>Техника:</b> {technique}
🥾 <b>Удары:</b> {kicks}
🛡 <b>Отбор мяча:</b> {ball_selection}
🏃 <b>Скорость:</b> {speed}
💨 <b>Выносливость:</b> {endurance}
🧍 <b>Позиция:</b> {position}

💪 <b>Общая сила</b>: {full_power}
</blockquote>
"""

async def send_message_approved_user(
    user_how_join: Character,
    club: Club 
) -> None:
    
    text = TEXT_TEMPLATE_JOIN_CHARATER.format(
        name = user_how_join.character_name,
        lvl = user_how_join.level,
        technique = user_how_join.technique,
        kicks = user_how_join.kicks,
        ball_selection = user_how_join.ball_selection,
        speed = user_how_join.speed,
        endurance = user_how_join.endurance,
        position = user_how_join.position,
        full_power = user_how_join.full_power
    )
    
    await bot.send_photo(
        photo=CHARACTER_SEND_OFFER_JOIN_TO_CLUB,
        chat_id=club.owner_id,
        caption=text,
        reply_markup=send_invite_to_join_club(
            character_id=user_how_join.id,
            club_id=club.id
        )
    )