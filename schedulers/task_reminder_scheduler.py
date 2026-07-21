import random
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from database.models.character import Character
from loader import bot
from services.character_service import CharacterService
from stats.stat_enum import StatisticsType

stat_type_desc = {
    StatisticsType.CONDUCT_3_TRAINING: "🏋️ Провести 3 тренування",
    StatisticsType.CONDUCT_5_TRAINING: "🏋️ Провести 5 тренувань",
    StatisticsType.CONDUCT_7_TRAINING: "🔥 Провести 7 тренувань",
    StatisticsType.RICH_SEMI_FINAL_BLITZ: "🥈 Вийти до півфіналу турніру Blitz",
    StatisticsType.PLAY_BLITZ: "⚡ Зіграти матч у Бліц-турнірі",
    StatisticsType.GOAL_IN_MATCH: "⚽ Забити гол у матчі",
    StatisticsType.MVP_TWO: "⭐ Стати MVP набравши 2+ очок",
    StatisticsType.MVP_TWO_HALF: "🌟 Стати MVP набравши 2.5+ очок",
    StatisticsType.MVP_THREE: "🏅 Стати MVP набравши 3+ очок",
    StatisticsType.REGISTER_ON_MATCH: "📝 Зареєструватися на матч",
    StatisticsType.RICH_FINAL_WIN_BLITZ: "🏆 Перемогти у фіналі бліц-турніру",
    StatisticsType.PLAY_2_BLITZ: "⚡ Зіграти у двух бліц турнірах",
}

class EducationCenterReminderText:
    texts = [
        "Не втрачайте шанс! 🎯 Ваш футболіст чекає на нові звершення у навчальному центрі. Ось ваші завдання:\n\n{tasks}",
        "Час розвивати свого футболіста! ⚽️ Виконайте завдання у навчальному центрі:\n\n{tasks}",
        "Герої створюються на тренуваннях! 🔥 Не забудьте виконати сьогоднішні завдання:\n\n{tasks}",
        "Ваш успіх залежить від дисципліни! 💪 Ось що потрібно зробити:\n\n{tasks}",
    ]

    @staticmethod
    def get_text_with_tasks(tasks: list[str]) -> str:
        tasks_str = "\n".join([f"▫️ {task}" for task in tasks])
        template = random.choice(EducationCenterReminderText.texts)
        return template.format(tasks=tasks_str)


class ReminderEducationCenter:
    task_times = ["10:00"]
    default_trigger_start = CronTrigger(hour=9)

    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()

    async def start(self):
        self.scheduler.add_job(
            func=self._start,
            trigger=self.default_trigger_start,
            misfire_grace_time=10
        )
        self.scheduler.start()

    async def _start(self):
        random_trigger = self.get_random_trigger
        self.scheduler.add_job(
            func=self.reminder_education_center,
            trigger=random_trigger,
            misfire_grace_time=10,
            id='education_reminder',
            replace_existing=True,
        )

    async def reminder_education_center(self):
        # Берем персонажей, у которых есть cipher и они активны
        characters = await CharacterService.get_all_characters()
        for character in characters:
            await self._send_message(character)

    async def _send_message(self, character: Character):
        try:
            if character.is_bot:
                return

            # получаем список заданий по cipher
            tasks_stats = CharacterService.decrypt_tier_cipher(character.tier_cipher)
            # переводим StatisticsType в человекочитаемый текст
            tasks_texts = [stat_type_desc.get(task, task.value) for task in tasks_stats]

            text = EducationCenterReminderText.get_text_with_tasks(tasks_texts)

            await bot.send_message(
                chat_id=character.characters_user_id,
                text=text
            )
        except Exception as e:
            print(e)

    @property
    def get_random_trigger(self) -> DateTrigger:
        now = datetime.now()
        current_date = now.date()

        random_time = random.choice(self.task_times)
        hour, minute = map(int, random_time.split(":"))

        run_date = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=hour, minutes=minute)

        # если выбранное время уже прошло сегодня — переносим на завтра
        if run_date <= now:
            run_date += timedelta(days=1)

        return DateTrigger(run_date=run_date)
