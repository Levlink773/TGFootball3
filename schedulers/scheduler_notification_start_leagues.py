import asyncio
import random
from aiogram import Bot
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database.models.character import Character

from services.character_service import CharacterService

from constants_leagues import TypeLeague, GetConfig

from logging_config import logger
from loader import bot

LEAGUE_MESSAGES: dict[TypeLeague, str] = {
    TypeLeague.BEST_LEAGUE: (
        "👑 <b>ЕвроКубки</b> стартують зараз!\n\n"
        "🔥 Тут грають тільки легенди — сильні, досвідчені, безкомпромісні.\n"
        "🗓 Турнір триватиме з <b>{start}</b> по <b>{end}</b>.\n"
        "Збирай команду мрії та доведи, що ти кращий з кращих! ⚽️🏆"
    ),
    TypeLeague.DEFAULT_LEAGUE: (
        "⚽ <b>Ліга</b> розпочалася!\n\n"
        "🎯 Ідеальний старт для тих, хто прагне піднятися вище.\n"
        "📅 Дати проведення: <b>{start} — {end}</b>.\n"
        "Грай сміливо та перемагай крок за кроком! 💪"
    ),
    TypeLeague.TOP_20_CLUB_LEAGUE: (
        "💼 <b>Кубок України</b> відкрився!\n\n"
        "🔝 Тільки обрані, тільки еліта — справжня битва титанів.\n"
        "📅 Період проведення: <b>{start} — {end}</b>.\n"
        "Викладися на повну, бо тут рахуються кожен гол і кожне очко! 🥇"
    ),
    TypeLeague.NEW_CLUB_LEAGUE: (
        "🌱 <b>Ліга Новачків</b> стартувала!\n\n"
        "🧃 Час показати себе і заявити про свій клуб на всю лігу.\n"
        "🗓 Матчі проходитимуть з <b>{start}</b> по <b>{end}</b>.\n"
        "Вперед, новачки — майбутнє саме за вами! 🍀"
    ),
}


class NotificationStartLeague:
    _bot: Bot = bot
    
    def __init__(self, type_league: TypeLeague) -> None:
        self.type_league = type_league
        
    @classmethod
    async def notify_start_league(cls, type_league: TypeLeague) -> None:
        obj = cls(type_league)
        all_characters = await CharacterService.get_all_users_not_bot()
        for character in all_characters:
            await obj._send_message(character)
            await asyncio.sleep(random.randint(1,2))
        
    async def _send_message(self, character: Character) -> None:
        try:
            await self._bot.send_message(
                chat_id=character.characters_user_id,
                text=self._get_text_league()
            )
        except Exception as E:
            logger.error(
                f"Error send notitication start league {character.character_name}"
            )
    
    def _get_text_league(self) -> str:
        config = GetConfig.get_config(self.type_league)
        start = config.DATETIME_START_LEAGUE.strftime("%d.%m")
        end = config.DATETIME_END_LEAGUE.strftime("%d.%m")

        template = LEAGUE_MESSAGES.get(self.type_league, None)
        if not template:
            return f"📢 Ліга {self.type_league.name} стартувала! \n<b>{start} - {end}</b>"

        return template.format(start=start, end=end)
    

class StartNotificationScheduler:
    
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()    

    async def start(self) -> None:
        for league_type in TypeLeague:
            await self._schedule_league_notification(league_type)
        self.scheduler.start()
        
    async def _schedule_league_notification(
        self, 
        league_type: TypeLeague
    ) -> None:
        config = GetConfig.get_config(league_type)
        self.scheduler.add_job(
            func=NotificationStartLeague.notify_start_league,
            args=[league_type],
            trigger=config.TRIGGER_SEND_MESSAGE_START,
            misfire_grace_time=10
        )