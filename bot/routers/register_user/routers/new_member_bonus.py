from aiogram import F, Router
from aiogram.types import  CallbackQuery

from database.models.character import Character

from constants import const_name_characteristics, TOTAL_POINTS_ADD_NEW_MEMBER
from config import POSITION_COEFFICIENTS, PositionCharacter

from services.character_service import CharacterService

bonus_new_member_router = Router()

TEMPLATE_TEXT_BONUS_NEW_MEMBER = """
⚙️ Гравцеві щойно були розподілені характеристики:

{stats_info}

💪 Завдяки цим параметрам гравець набрав нову бойову форму та став ще небезпечнішим на полі.
<b>Настав час показати себе у справжньому матчі!</b> ⚽🔥

📊 Поточна сила: <b>{total_power:.2f}</b>
"""
TEMPLATE_STAT_ADD = "- {stat_name}: <b>{stat_value}</b>"


@bonus_new_member_router.callback_query(
    F.data == "get_new_member_bonus"
)
async def get_new_member_bonus_handler(
    query: CallbackQuery,
    character: Character,
):
    if character.full_power > TOTAL_POINTS_ADD_NEW_MEMBER/2:
        await query.answer(
            text = "Вам не потрібно отримувати бонуси новачка, ви вже досвідчений гравець!",
        )
        return await query.message.delete()
    stats = distribute_stats(character.position_enum)
    for stat, points in stats.items():
        await CharacterService.update_character_characteristic(
            character_id=character.id,
            type_characteristic = stat,
            amount_add_points = points 
        )
    text_bonus = await get_text_bonus_new_member(
        character_id=character.id,
        stats=stats
    )
    # await query.message.answer(
    #     text = text_bonus
    # )
    
async def get_text_bonus_new_member(
    character_id: int,
    stats: dict[str, int],
) -> str:
    
    character = await CharacterService.get_character_by_id(
        character_id=character_id
    )
    stats_info = [ 
            TEMPLATE_STAT_ADD.format(
                stat_name=const_name_characteristics.get(stat, stat),
                stat_value=points
            )
            for stat, points in stats.items()
        ]
    
    return TEMPLATE_TEXT_BONUS_NEW_MEMBER.format(
        stats_info="\n".join(stats_info),
        total_power=character.full_power
    )
    

def distribute_stats(
    position: PositionCharacter, 
) -> dict[str, int]:
    base_coeffs = POSITION_COEFFICIENTS[position]
    
    full_coeffs = {
        stat: base_coeffs.get(stat, 1.0)
        for stat in const_name_characteristics
    }

    coeff_sum = sum(full_coeffs.values())

    raw_distribution = {
        stat: int((coeff / coeff_sum) * TOTAL_POINTS_ADD_NEW_MEMBER)
        for stat, coeff in full_coeffs.items()
    }

    current_sum = sum(raw_distribution.values())
    leftover = TOTAL_POINTS_ADD_NEW_MEMBER - current_sum

    if leftover > 0:
        sorted_stats = sorted(
            full_coeffs.items(),
            key=lambda item: ((item[1] / coeff_sum) * TOTAL_POINTS_ADD_NEW_MEMBER) % 1,
            reverse=True
        )
        for stat, _ in sorted_stats:
            if leftover == 0:
                break
            raw_distribution[stat] += 1
            leftover -= 1

    return raw_distribution