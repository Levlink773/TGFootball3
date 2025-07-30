from enum import Enum

from aiogram import Bot

from bot.keyboards.gym_keyboard import no_energy_keyboard

from database.models.character import Character

from constants import LOW_ENERGY_PHOTO

from loader import bot
from logging_config import logger

from .base_event import BaseEventListener


class TypeLowEnergy(int, Enum):
    LOW_ENERGY = 20
    ZERO_ENERGY = 0
    
TEXT_LOW_ENERGY = """
⚠️ <b>Енергія майже на нулі!</b>  

🔋 Ваш рівень енергії впав нижче критичної позначки, і це може вплинути на ваш прогрес у грі. Не дайте цьому зупинити вас!  

✅ <i>Без перерви на відновлення — грайте без зупинок!</i>  
✅ <i>Забезпечте собі перевагу над суперниками!</i>  

⚡️ <b>Не зупиняйтесь!</b>  
Поповніть енергію прямо зараз, щоб залишатися в грі та досягати нових висот!  
"""
   
TEXT_ZERO_ENERGY = """
⚠️ <b>Енергія на нулі!</b>

🔋 Ваш рівень енергії впав нижче критичної позначки, і це може вплинути на ваш прогрес у грі. Не дайте цьому зупинити вас!

✅ <i>Швидке поповнення енергії — більше сил для нових звершень!</i>
✅ <i>Без перерви на відновлення — грайте без зупинок!</i>
✅ <i>Забезпечте собі перевагу над суперниками!</i>

⚡ <b>Не зупиняйтесь!</b>
Поповніть енергію прямо зараз, щоб залишатися в грі та досягати нових висот!
"""
    
TEXT_LOW_ENERGY = {
    TypeLowEnergy.LOW_ENERGY: TEXT_LOW_ENERGY,
    TypeLowEnergy.ZERO_ENERGY: TEXT_ZERO_ENERGY,
}


class EnergyEventListener(BaseEventListener):
    _bot: Bot = bot 
    _by_energy_keyboard = no_energy_keyboard()
    
    async def handle_event(self, character: Character) -> None:
        if not self.valide_low_energy(character):
            return
        type_low_energy = self.get_type_energy(character)
        await self._send_message(character, type_low_energy)
        
    async def _send_message(
        self, 
        character: Character,
        type_low_energy: TypeLowEnergy
    ) -> None:
        text = TEXT_LOW_ENERGY[type_low_energy]
        
        try:
            await self._bot.send_photo(
                photo        = LOW_ENERGY_PHOTO,
                chat_id      = character.characters_user_id,
                caption      = text,
                reply_markup = self._by_energy_keyboard
            )
        except Exception as E:
            logger.error(
                f"Error send message to character: {character.name}"
            )
            
    @staticmethod
    def valide_low_energy(character: Character) -> bool:
        if character.current_energy < TypeLowEnergy.LOW_ENERGY:
            return True
        
        if not character.current_energy:
            return True
        
        return False
    
    @staticmethod
    def get_type_energy(character: Character) -> TypeLowEnergy:
        if not character.current_energy:
            return TypeLowEnergy.ZERO_ENERGY
        
        if character.current_energy < TypeLowEnergy.LOW_ENERGY:
            return TypeLowEnergy.LOW_ENERGY
