from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from bot.keyboards.vip_pass import (
    select_type_vip_pass
)

from database.models.character import Character

from services.vip_pass_service import VipPassService
from services.club_service import ClubService

from logging_config import logger
from loader import bot

from constants import END_VIP_PASS_PHOTO


class VipPassScheduler:
    
    TEXT_TEMPLATE = """
🔥 <b>Ваш VIP-пас закінчився!</b>

🎟️ Але не хвилюйтесь, адже у вас є шанс знову стати VIP-гравцем та отримати всі переваги:

✅ <i>🔋 300 енергії +150 щодня! Тепер 300 енергії замість 150 — більше можливостей для досягнення успіху!</i>  
✅ <i>Х2 нагород з навчального центру — вдвічі більше корисних бонусів для твого прогресу!</i>  
✅ <i>+5% успішності тренування — будь упевнений у своєму успіху і швидше досягай нових висот!</i>  
✅ <i>VIP-статус — тепер твій нік буде виділятися, показуючи всім, хто тут справжній майстер гри!</i>  

⚡ <b>Не втрачайте шанс бути на вершині!</b>  
Продовжіть VIP-пас прямо зараз і отримуйте ще більше задоволення від гри!  

"""
    
    def __init__(self, character: Character):
        self.scheduler = AsyncIOScheduler()
        self.character = character
        
        self._user_id: int = character.characters_user_id
        
        self._end_time: datetime = character.vip_pass_expiration_date
        
    async def _send_message(self):
        try:
            await bot.send_photo(
                chat_id      =self._user_id,
                photo        = END_VIP_PASS_PHOTO,
                caption      = self.TEXT_TEMPLATE,
                reply_markup = select_type_vip_pass()
            )
        except Exception as E:
            logger.error(f"Failed to send message to {self.character.name}\nError: {E}")
            
    async def start_taimer(self):
        self.scheduler.add_job(
            func = self._send_message,
            trigger = self.trigger_end_date_vip_pass,
            name = f"end_time_vip_pass_{self.character.characters_user_id}",
            misfire_grace_time=10,
        )
        self.scheduler.start()

    
    @property
    def trigger_end_date_vip_pass(self):
        return DateTrigger(run_date=self._end_time)
    
    
class VipPassSchedulerService:
    def __init__(self):
        self._character_vip_pass_service = VipPassService()
        self._club_service = ClubService()

    async def start_timers(self):
        characters = await self._character_vip_pass_service.get_have_vip_pass_characters()
        for character in characters:
            vip_pass_scheduler = VipPassScheduler(character)
            await vip_pass_scheduler.start_taimer() 