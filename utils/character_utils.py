from database.models.character import Character
from services.character_service import CharacterService

from sqlalchemy.orm.exc import DetachedInstanceError

from constants import Gender, REFERAL_EXP
from loader import bot

def get_character_text(character: Character) -> str:
    gender_specific_text = {
        Gender.MAN: "Він завжди перемагає!",
        Gender.WOMAN: "Вона - зірка на полі!"
    }

    current_level = character.level
    if current_level >= len(character.LEVEL_THRESHOLDS):
        next_level_threshold = "∞"
    else:
        next_level_threshold = character.LEVEL_THRESHOLDS[current_level-1]

    level_text = f"<b>🏆 Рівень:</b> {character.level} [{character.exp}/{next_level_threshold}]"
    
    try:
        t_shirt_text = character.t_shirt.name if character.t_shirt else "Не экипировано"
        shorts_text = character.shorts.name if character.shorts else "Не экипировано"
        gaiters_text = character.gaiters.name if character.gaiters else "Не экипировано"
        boots_text = character.boots.name if character.boots else "Не экипировано"
    except DetachedInstanceError:
        t_shirt_text = "Не экипировано"
        shorts_text =  "Не экипировано"
        gaiters_text =  "Не экипировано"
        boots_text =  "Не экипировано" 

    character_text_template = f"""
<b>⚽ Персонаж:</b> {character.character_name}

{level_text}
<b>💰 Монети:</b> {character.money}

<b>👤 Стать:</b> {character.gender_enum.value}
<b>🏅 Позиція:</b> {character.position_description} 

<b>🎯 Техніка:</b> {character.effective_technique:.1f}
<b>🥋 Удари:</b> {character.effective_kicks:.1f}
<b>🛡️ Відбір м’яча:</b> {character.effective_ball_selection:.1f}
<b>⚡ Швидкість:</b> {character.effective_speed:.1f}
<b>🏃 Витривалість:</b> {character.effective_endurance:.1f}

<b>💪 Сумарна сила:</b> {character.full_power:.1f}

<b>🔋 Енергія:</b> {character.current_energy}/{character.max_energy}

<b>👕 Футболка:</b> {t_shirt_text}
<b>🩳 Шорти:</b> {shorts_text}
<b>🧦 Гетри:</b> {gaiters_text}
<b>👟 Бутси:</b> {boots_text}

<i>{gender_specific_text[character.gender_enum]}</i>
"""

    return character_text_template.strip()


async def get_referal_text(my_character: Character):
    all_referals_character = await CharacterService.get_my_referals(character_user_id=my_character.characters_user_id)
    active_referals = [referal for referal in all_referals_character if referal.exp >= REFERAL_EXP]
    
    bot_me = await bot.get_me()
    referal_link = f"https://t.me/{bot_me.username}?start=ref_{my_character.characters_user_id}"
    
    text = f"""
🌀 Приєднуйся до реферальної системи!
Запрошуй друзів та отримуй цінні бонуси! 🎉

🔋 300 енергії та 💰 300 монет за кожного друга, який набере {REFERAL_EXP} очок досвіду в грі! 🎮

👥 Твої реферали:

Зареєстровано: {len(all_referals_character)}
Отримали {REFERAL_EXP} очок досвіду: {len(active_referals)}

🎯 Твоє реферальне посилання:
{referal_link}

Чим більше друзів - тим більше нагород! Не прогав свій шанс прокачати свого персонажа швидше! 💪
    
    """
    return text