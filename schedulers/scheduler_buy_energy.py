import random
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from database.models.reminder_character import ReminderCharacter

from services.reminder_character_service import RemniderCharacterService
from services.character_service import CharacterService

from loader import bot

class TextReminder:
    texts = [
        "Привіт, ⚽️! Здається, ваш футболіст дуже скучив за тренуваннями! 🏃‍♂️💨 Заходьте, щоб підтримувати форму та готуватись до наступних матчів! 💪",
        "Ей, чемпіон! 🏆 Ви вже давно не тренувалися, а ваша команда розраховує на вас! Час повернутися до гри та показати, хто тут зірка футболу! 🌟",
        "Ну що, відпочинок вдався? 😏 Ваш футболіст вже майже забув, як виглядає м'яч! ⚽️ Швиденько на тренування — час повернути легендарну форму! 🥅🔥",
        "Ой-ой! Ваша команда вже починає програвати через нестачу тренувань. 😱 Поверніться до гри, поки суперники не забрали всі трофеї! 🥇",
        "Легенди не створюються без зусиль! 🌟 Пора вашому футболісту повернутись на поле та показати, чому саме він майбутній чемпіон! ⚡️ Не відкладайте, тренування чекають! 💪",
        "Схоже, ваш футболіст перейшов у режим сплячки. 🛌💤 Час розбудити його та згадати, як круто бути в топі! ⚽️ Давайте на тренування — в гру! 🔥"
    ]

    @staticmethod
    def get_random_text():
        return random.choice(TextReminder.texts)

class ReminderBuyEnergy:
    
    task_times = ["09:00", "12:00", "18:00", "21:00"]
    default_trigger_start = CronTrigger(hour=8)

    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
    
    async def start(self):
        self.scheduler.add_job(
            func    = self._start, 
            trigger = self.default_trigger_start,
            misfire_grace_time = 10
        )
        self.scheduler.start()
    
    
    async def _start(self):
        random_trigger = self.get_random_trigger
        self.scheduler.add_job(
            func    = self.reminder_buy_energy,
            trigger = random_trigger,
            misfire_grace_time = 10
        )
        
    async def reminder_buy_energy(self):
        characters_not_training = await RemniderCharacterService.get_characters_not_training()
        for reminder_character in characters_not_training:
            await self._send_message(reminder_character)

    async def _send_message(self, reminder_character: ReminderCharacter):
        try:
            character = await CharacterService.get_character_by_id(
                character_id = reminder_character.character_id
            )
            if character.is_bot:
                return
            
            await bot.send_message(
                chat_id = character.characters_user_id,
                text = TextReminder.get_random_text()
            )
        except Exception as E:
            print(E)
        
    @property
    def get_random_trigger(self) -> DateTrigger:
        current_date = datetime.now().date()
        random_time = random.choice(self.task_times)
        hour, minute = map(int, random_time.split(":"))
        
        run_date = datetime.combine(current_date, datetime.min.time())
        run_date += timedelta(hours=hour, minutes=minute)
        return DateTrigger(run_date=run_date)
