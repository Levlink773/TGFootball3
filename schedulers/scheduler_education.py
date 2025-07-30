from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from datetime import datetime, timedelta

from database.models.character import Character
from services.character_service import CharacterService

from loader import bot
from config import EPOCH_ZERO


class EducationRewardReminderScheduler():
    scheduler = AsyncIOScheduler()    
    bot = bot

    TEMPLATE_TEXT_REWARD_EDUCATION = """Не забудьте отримати нагороди за навчання!"""

    
    async def _send_character_remind_reward_message(self, character_user_id: int):
        try:
            await self.bot.send_message(
                chat_id=character_user_id,
                text=self.TEMPLATE_TEXT_REWARD_EDUCATION
            )
        except:
            pass
    async def add_job_remind(self, character: Character,
                             time_get_reward: datetime):
        
        self.scheduler.add_job(func=self._send_character_remind_reward_message, 
                               args=[character.characters_user_id],
                               trigger='date',
                               run_date = time_get_reward,
                               misfire_grace_time = 10

                               )
        

    async def start_reminder(self):
        current_time = datetime.now()
        one_month_ago = current_time - timedelta(days=30)
        all_not_bot_users = await CharacterService.get_all_users_not_bot()
        for character in all_not_bot_users:
            if character.reminder.education_reward_date == EPOCH_ZERO:
                continue
            if character.reminder.education_reward_date < one_month_ago:
                continue
            
            if character.reminder.education_reward_date > current_time:
                await self.add_job_remind(
                    character=character,
                    time_get_reward=character.reminder.education_reward_date
                )
            else:
                await self._send_character_remind_reward_message(character.characters_user_id)
        self.scheduler.start()
