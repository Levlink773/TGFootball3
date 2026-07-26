"""Напоминание про нагороду навчального центру.

Раньше это был DateTrigger на каждого персонажа, который перевзводился в
bot/routers/gym/education_center.py после КЛЕЙМА В БОТЕ. Клейм из Mini App
(webapp_api) перевзвести его не мог: это отдельный процесс со своей памятью —
значит игрок, забравший награду в приложении, больше НИКОГДА не получал
напоминания.

Sweep по состоянию в БД чинит это и заодно убирает обход всех персонажей
при старте. Атомарный claim (claim_education_reminder_send) не тронут — это
единственная корректная at-most-once гарантия в проекте.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from services.character_service import CharacterService

from logging_config import logger
from utils.notify import notify


class EducationRewardReminderScheduler:
    TEMPLATE_TEXT_REWARD_EDUCATION = (
        "🏫 <b>Навчальний центр</b>\n\n"
        "Нагорода за навчання вже готова — забирай досвід, монети та енергію! 🎓"
    )

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    async def start_reminder(self):
        self.scheduler.add_job(
            func=self.remind_due,
            trigger=CronTrigger(minute=10),
            misfire_grace_time=600,
        )
        self.scheduler.start()

    async def remind_due(self):
        characters = await CharacterService.get_characters_education_reward_due()
        sent = 0
        for character in characters:
            # Claim-before-send: флаг в БД гарантирует не больше одного
            # напоминания на цикл награды, даже при рестарте или дубле процесса.
            if not await CharacterService.claim_education_reminder_send(
                character.characters_user_id
            ):
                continue
            if await notify(
                character,
                self.TEMPLATE_TEXT_REWARD_EDUCATION,
                screen="training",
                button_text="🏫 До навчального центру",
            ):
                sent += 1
        logger.info(f"Education reward reminder: sent {sent} of {len(characters)} due")
