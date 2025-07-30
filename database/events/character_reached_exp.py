import asyncio
from aiogram import Bot

from database.models.character import Character

from services.character_service import CharacterService

from loader import bot

from .base_event import BaseEventListener

semaphore = asyncio.Semaphore(1) 

class ExpEventListener(BaseEventListener):
    TEXT_TEMPLATE  = "EXP"
    ENERGY_REFERAL = 150
    MONEY_REFERAL  = 20
    REFERAL_EXP = 20
    
    _bot: Bot = bot
    
    async def handle_event(self, character: Character):
        async with semaphore:
            if not self._is_valid(character):
                return
            
            character_referal = await CharacterService.get_character(character_user_id=character.referal_user_id)
            
            await CharacterService.edit_character_energy(
                character_id  = character_referal.id,
                amount_energy = self.ENERGY_REFERAL
            )
            await CharacterService.update_money_character(
                character_id = character_referal.id,
                amount_money_adjustment = self.MONEY_REFERAL
            )
            text = f"""
    🏅 Ваш реферал [{character.character_name}] набрав {self.REFERAL_EXP} очок досвіду!

    Ви отримуєте {self.ENERGY_REFERAL} енергії та 20 монет!
    """
            
            try:    
                await bot.send_message(
                    chat_id=character.referal_user_id,
                    text=text
                )
            except Exception as e:
                print(f"Error sending message: {e}")
            
            await CharacterService.edit_status_reward_by_referal(
                character_user_id = character.characters_user_id
            )

    def _is_valid(self, character: Character) -> bool:
        if not character.referal_user_id:
            return False
        
        if character.exp < 20:
            return False
        
        if character.referral_award_is_received:
            return False
        
        return True


