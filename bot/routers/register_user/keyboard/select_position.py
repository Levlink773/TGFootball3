from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.routers.register_user.callbacks.create_character_callbacks import (
    SelectGender,
    SelectPositionCharacter, 
    CreateCharacter
)

from constants import Gender, PositionCharacter

from database.models.character import Character

def set_gender_keyboard() -> InlineKeyboardMarkup:
    return (InlineKeyboardBuilder()
            .button(text = "👨🏼‍🦱 Чоловік", callback_data = SelectGender(gender=Gender.MAN))
            .button(text = "👩🏼‍🦰 Жінка", callback_data = SelectGender(gender=Gender.WOMAN))
            .adjust(1)
            .as_markup()
            )



def select_role_character(gender_character: Gender) ->InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    
    keyboard.button(
        text= "Захисник" if gender_character == Gender.MAN else "Захисниця",
        callback_data=SelectPositionCharacter(position=PositionCharacter.DEFENDER)
    )
    keyboard.button(
        text= "Воротар" if gender_character == Gender.MAN else "Воротарка",
        callback_data=SelectPositionCharacter(position=PositionCharacter.GOALKEEPER)
    )
    keyboard.button(
        text= "Півзахисник" if gender_character == Gender.MAN else "Півзахисниця",
        callback_data=SelectPositionCharacter(position=PositionCharacter.MIDFIELDER)
    )
    keyboard.button(
        text= "Нападник" if gender_character == Gender.MAN else "Нападниця",
        callback_data=SelectPositionCharacter(position=PositionCharacter.ATTACKER)
    )
    keyboard.button(
        text="⬅️ Вибрати іншу стать", 
        callback_data="back_to_select_gender"
    )
    return keyboard.adjust(2,2,1).as_markup()

def create_character(character: Character) -> InlineKeyboardMarkup:
    return (InlineKeyboardBuilder()
            .button(text = "✅ Вибрати цього персонажа", 
                    callback_data = CreateCharacter(gender=character.gender_enum,
                                                    position=character.position_enum))
            .button(text = "🔄 Вибрати іншу позицію",
                    callback_data = "select_other_position")
            .adjust(1)
            .as_markup()
            )

