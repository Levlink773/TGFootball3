import asyncio
from datetime import datetime, timedelta

from apscheduler.triggers.date import DateTrigger

from database.models.club import Club
from database.models.character import Character

from services.league_services.league_service import LeagueService
from services.match_character_service import MatchCharacterService

from logging_config import logger
from loader import bot
from bot.keyboards.league_keyboard import keyboard_to_join_character_to_fight
from constants import JOIN_TO_FIGHT

from utils.rate_limitter import rate_limiter

# Тайминг напоминаний о регистрации на матч (Max 26.07): за 40 / 15 / 5 минут.
REMINDER_MINUTES = (40, 15, 5)
# Не класть напоминание вплотную к общей рассылке-приглашению: у ЕвроКубков она
# идёт в T-40, у Ліги Новачків — в T-15, иначе два сообщения в одну секунду.
_SKIP_NEAR = timedelta(minutes=3)


def schedule_match_reminders(
    scheduler,
    user_sender: "UserSender",
    start_time_fight: datetime,
    blast_at: datetime = None,
    misfire_grace_time: int = 10,
) -> int:
    """Повесить напоминания T-40 / T-15 / T-5 для одного матча.

    Один хелпер на все четыре лиги вместо копии блока в каждой.
    Возвращает число реально поставленных джоб (для тестов).
    """
    now = datetime.now()
    scheduled = 0
    for minutes in REMINDER_MINUTES:
        remind_at = start_time_fight - timedelta(minutes=minutes)
        if remind_at <= now:
            continue
        if blast_at and abs(remind_at - blast_at) < _SKIP_NEAR:
            continue
        scheduler.add_job(
            user_sender.send_reminder,
            trigger=DateTrigger(remind_at),
            kwargs={"minutes_left": minutes},
            misfire_grace_time=misfire_grace_time,
        )
        scheduled += 1
    return scheduled


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
        
    # Свой текст на каждый тир — иначе к третьему сообщению глаз замыливается.
    TEMPLATE_REMINDER = {
        40: (
            "⏰ Матч <b>{name_first_club}</b> — <b>{name_second_club}</b> вже за <b>40 хвилин</b>!\n\n"
            "Ти ще не в заявці. Тисни кнопку — і ти в складі. ⚽️"
        ),
        15: (
            "⚡️ <b>15 хвилин</b> до матчу <b>{name_first_club}</b> — <b>{name_second_club}</b>!\n\n"
            "Без реєстрації ти не вийдеш на поле. Встигни! ⏳"
        ),
        5: (
            "🚨 <b>5 хвилин!</b> Матч <b>{name_first_club}</b> — <b>{name_second_club}</b> ось-ось почнеться.\n\n"
            "Останній шанс зареєструватись! 🔥"
        ),
    }

    async def send_messages_to_users(self):
        await self._post_init()

        for character in self.characters:
            await self.__send_message(character)

    async def send_reminder(self, minutes_left: int):
        # Текстовый пинок без фото. Зарегистрированным не шлём (Max 26.07):
        # один запрос на тир, а не по запросу на игрока.
        await self._post_init()
        registered = {
            mc.character_id
            for mc in await MatchCharacterService.get_characters_from_match(self.match_id)
        }
        for character in self.characters:
            if character.id in registered or character.is_blocked:
                continue
            await self.__send_reminder(character, minutes_left)

    @rate_limiter
    async def __send_reminder(self, character: Character, minutes_left: int):
        try:
            if not character.is_bot:
                await asyncio.sleep(1)
                await bot.send_message(
                    chat_id=character.characters_user_id,
                    text=self.TEMPLATE_REMINDER[minutes_left].format(
                        name_first_club=self.first_club.name_club,
                        name_second_club=self.second_club.name_club,
                    ),
                    reply_markup=keyboard_to_join_character_to_fight(match_id=self.match_id),
                )
        except Exception as E:
            logger.error(f"Failed reminder to {character.characters_user_id}\nError: {E}")

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
