import asyncio

from database.models.club import Club
from database.models.character import Character

from services.league_services.league_service import LeagueService

from logging_config import logger
from loader import bot
from bot.keyboards.league_keyboard import keyboard_to_join_character_to_fight
from constants import JOIN_TO_FIGHT

from utils.rate_limitter import rate_limiter

class UserSender:
    TEMPLATE_JOIN_TO_FIGHT = """
    ⚽️ Матч між командами <b>{name_first_club}</b> та <b>{name_second_club}</b>! 
    
    """
    
    messages_queue = asyncio.Queue()
    
    
    def __init__(self, 
                 match_id: int) -> None:
        self.match_id = match_id
        self.characters = []
        self.first_club = None
        self.second_club = None
        
    async def _post_init(self):
        league_fight = await LeagueService.get_league_fight(self.match_id)
        self.first_club: Club = league_fight.first_club
        self.second_club: Club = league_fight.second_club
        self.characters = [character for character in (self.second_club.characters + self.first_club.characters) if not character.is_bot] 
        
    async def send_messages_to_users(self):
        await self._post_init()
        
        for character in self.characters:
            await self.__send_message(character)

    def __get_text(self):
        return self.TEMPLATE_JOIN_TO_FIGHT.format(
            name_first_club  = self.first_club.name_club,
            name_second_club = self.second_club.name_club
        )

    @rate_limiter
    async def __send_message(self, character: Character):
        try:
            
            if not character.is_bot:
                await asyncio.sleep(1)
                await bot.send_photo(
                    chat_id=character.characters_user_id,
                    photo=JOIN_TO_FIGHT,
                    caption= self.__get_text(),
                    reply_markup=keyboard_to_join_character_to_fight(
                        match_id=self.match_id
                    )
                )
                logger.info(f"ОТПРАВИЛ СООБЩЕНИЕ {character.character_name} ID USER {character.characters_user_id}")
        except Exception as E:
            logger.error(f"Failed to send message to {character.characters_user_id}\nError: {E}")
