from dataclasses import dataclass
from typing import Callable, Any, Dict
from abc import ABC, abstractmethod

from aiogram.types import Message, InputMediaPhoto

from bot.keyboards.gym_keyboard import back_to_education_task_service
from constants import EDUCATION_TASK_REWARD
from database.models.character import Character
from services.character_service import CharacterService
from services.statistics_service import StatisticsService
from stats.stat_enum import StatisticsType

# --- базовый класс (оставляем почти как был) ---
class BaseStatistics(ABC):
    def __init__(self, char: Character):
        self.char = char

    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError()

    def describe(self):
        done, progress = self.statistics_result()
        if done:
            return self.describe_statistics_success()
        return self.describe_statistics(progress)

    @abstractmethod
    def describe_statistics(self, result):
        raise NotImplementedError()

    @abstractmethod
    def describe_statistics_success(self):
        raise NotImplementedError()

    @abstractmethod
    def text_get_button(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def stat_type(self) -> StatisticsType:
        raise NotImplementedError()

    @abstractmethod
    def statistics_result(self) -> tuple[bool, Any]:
        raise NotImplementedError()

    @abstractmethod
    async def reward_stat(self, message: Message):
        raise NotImplementedError()

# --- Универсальная реализация для большинства статистик ---
@dataclass
class GenericStatistics(BaseStatistics):
    # обязательные
    _stat_type: StatisticsType
    _description_text: str
    _threshold: float
    # награды
    energy: int = 0
    money: int = 0
    # шаблоны (можно передать строку с формат-плейсхолдерами)
    describe_template: str = ""
    success_template: str = ""
    button_text_template: str = "🎁 Забрати нагороду"
    reward_caption_template: str = "🏅 Ви отримали нагороду!"
    # как получать текущее значение прогресса (функция char -> number)
    progress_getter: Callable[[Character], Any] = lambda c: 0

    def __init__(
        self,
        char: Character,
        stat_type: StatisticsType,
        description_text: str,
        threshold: float = 1,
        energy: int = 0,
        money: int = 0,
        describe_template: str = "",
        success_template: str = "",
        button_text_template: str = "🎁 Забрати нагороду",
        reward_caption_template: str = "🏅 Ви отримали нагороду!",
        progress_getter: Callable[[Character], Any] = lambda c: 0,
    ):
        super().__init__(char)
        self._stat_type = stat_type
        self._description_text = description_text
        self._threshold = threshold
        self.energy = energy
        self.money = money
        self.describe_template = describe_template or "{progress}"
        self.success_template = success_template or "Ви виконали завдання! Натискайте «{button}» щоб отримати нагороду."
        self.button_text_template = button_text_template
        self.reward_caption_template = reward_caption_template
        self.progress_getter = progress_getter

    # --- интерфейс ---
    def description(self) -> str:
        return self._description_text

    def stat_type(self) -> StatisticsType:
        return self._stat_type

    def statistics_result(self) -> tuple[bool, Any]:
        progress = self.progress_getter(self.char) or 0
        done = progress >= self._threshold
        return done, progress

    def describe_statistics(self, progress):
        remaining = max(0, int(self._threshold - progress))
        return self.describe_template.format(progress=progress, remaining=remaining, threshold=self._threshold)

    def describe_statistics_success(self):
        return self.success_template.format(button=self.text_get_button(), threshold=self._threshold)

    def text_get_button(self) -> str:
        return self.button_text_template.format(threshold=self._threshold)

    async def reward_stat(self, message: Message):
        # проверяем, не забрана ли уже награда
        already = any(s.stat_type == self.stat_type() for s in self.char.statistics)
        if already:
            return await message.answer(chat_id=self.char.id, text="ℹ️ Ви вже забирали нагороду за це завдання.")

        # выдать энергию
        if self.energy:
            await CharacterService.edit_character_energy(self.char.id, self.energy)

        # выдать деньги — пытливый, но безопасный способ: ищем подходящий метод
        if self.money:
            await CharacterService.update_money_character(self.char.id, self.money)

        # сохраняем статистику
        await StatisticsService.save_statistics(self.char.id, self.stat_type())

        # редактируем медиа/сообщение в чат
        caption = self.reward_caption_template.format(energy=self.energy, money=self.money, threshold=self._threshold)
        await message.edit_media(
            media=InputMediaPhoto(media=EDUCATION_TASK_REWARD, caption=caption),
            reply_markup=back_to_education_task_service(),
        )

# --- Список конфигураций (удобно редактировать/добавлять новые) ---
# Каждая запись — фабрика: получает Character и возвращает экземпляр GenericStatistics
def _progress_getter_attr(attr: str) -> Callable[[Character], Any]:
    return lambda c: getattr(c, attr, 0)

STAT_REGISTRY: Dict[StatisticsType, Callable[[Character], BaseStatistics]] = {
    # --- Tier 1 ---
    StatisticsType.CONDUCT_3_TRAINING: lambda ch: GenericStatistics(
        ch,
        stat_type=StatisticsType.CONDUCT_3_TRAINING,
        description_text="Проведи 3 тренування — отримай +50⚡ енергії!",
        threshold=3,
        energy=50,
        describe_template="Ви вже провели {progress} тренувань! Залишилось ще {remaining} до мети 🎯",
        success_template="🔥 Вітаємо, чемпіоне! Ви провели 3 тренування 💪 Натискайте «{button}» та забирайте свою нагороду — +50⚡ енергії!",
        button_text_template="🎁 Забрати нагороду за 3 тренування",
        reward_caption_template="🏅 Ви отримали +{energy}⚡ енергії! Час витратити її з користю 😉",
        progress_getter=_progress_getter_attr("count_go_to_gym"),
    ),
    StatisticsType.CONDUCT_5_TRAINING: lambda ch: GenericStatistics(
        ch,
        stat_type=StatisticsType.CONDUCT_5_TRAINING,
        description_text="Проведи 5 тренувань — отримай +75⚡ енергії!",
        threshold=5,
        energy=75,
        describe_template="Ви вже провели {progress} тренувань! Залишилось ще {remaining} до мети 🎯",
        button_text_template="🎁 Забрати нагороду за 5 тренувань",
        reward_caption_template="🏅 Ви отримали +{energy}⚡ енергії!",
        progress_getter=_progress_getter_attr("count_go_to_gym"),
    ),
    StatisticsType.CONDUCT_7_TRAINING: lambda ch: GenericStatistics(
        ch,
        stat_type=StatisticsType.CONDUCT_7_TRAINING,
        description_text="Проведи 7 тренувань — отримай +100⚡ енергії!",
        threshold=7,
        energy=100,
        describe_template="Ви вже провели {progress} тренувань! Залишилось ще {remaining} до мети 🎯",
        button_text_template="🎁 Забрати нагороду за 7 тренувань",
        reward_caption_template="🏅 Ви отримали +{energy}⚡ енергії!",
        progress_getter=_progress_getter_attr("count_go_to_gym"),
    ),

    StatisticsType.PLAY_BLITZ: lambda ch: GenericStatistics(
        ch,
        stat_type=StatisticsType.PLAY_BLITZ,
        description_text="Зіграйте турнір — забери +20⚡ енергії!",
        threshold=1,
        energy=20,
        describe_template="Ви зіграли {progress} турнірів. Ще трішки до першої перемоги 🏆",
        button_text_template="🎁 Забрати нагороду за турнір",
        reward_caption_template="🏅 Ви отримали +{energy}⚡ енергії! Попереду ще більше турнірів 💥",
        progress_getter=_progress_getter_attr("count_play_blitz"),
    ),

    StatisticsType.PLAY_2_BLITZ: lambda ch: GenericStatistics(
        ch,
        stat_type=StatisticsType.PLAY_2_BLITZ,
        description_text="Зіграйте 2 турніри — отримайте +70⚡ енергії!",
        threshold=2,
        energy=70,
        describe_template="Ви зіграли {progress} турнірів. Ще {remaining} до нагороди 🏆",
        button_text_template="🎁 Забрати нагороду за 2 турніри",
        reward_caption_template="🏅 Ви отримали +{energy}⚡ енергії!",
        progress_getter=_progress_getter_attr("count_play_blitz"),
    ),

    # --- Tier 2 ---
    StatisticsType.GOAL_IN_MATCH: lambda ch: GenericStatistics(
        ch,
        stat_type=StatisticsType.GOAL_IN_MATCH,
        description_text="Забий гол у матчі — отримай +50⚡ енергії!",
        threshold=1,
        energy=50,
        describe_template="Ви забили {progress} гол(ів). Чекаємо ще більше ⚽",
        button_text_template="🎁 Забрати нагороду за гол",
        reward_caption_template="🏅 Ви отримали +{energy}⚡ енергії!",
        progress_getter=_progress_getter_attr("count_goal_on_match"),
    ),
    StatisticsType.RICH_SEMI_FINAL_BLITZ: lambda ch: GenericStatistics(
        ch,
        stat_type=StatisticsType.RICH_SEMI_FINAL_BLITZ,
        description_text="Дійди до півфіналу — отримай +50⚡ енергії!",
        threshold=1,
        energy=50,
        describe_template="Ви вже доходили до півфіналу {progress} раз(ів)! Ще трішки до фіналу 🏆",
        button_text_template="🎁 Забрати нагороду за півфінал",
        reward_caption_template="🏅 Ви отримали +{energy}⚡ енергії! Наступна зупинка — фінал 🏟️",
        progress_getter=_progress_getter_attr("count_rich_semi_final_blitz"),
    ),
    StatisticsType.RICH_FINAL_WIN_BLITZ: lambda ch: GenericStatistics(
        ch,
        stat_type=StatisticsType.RICH_FINAL_WIN_BLITZ,
        description_text="Переможи у бліц-турнірі — отримай +100⚡ енергії!",
        threshold=1,
        energy=100,
        describe_template="Ви виграли {progress} турнір(ів). Чудовий результат! 🏆",
        button_text_template="🎁 Забрати нагороду за перемогу у бліці",
        reward_caption_template="🏅 Ви отримали +{energy}⚡ енергії!",
        progress_getter=_progress_getter_attr("count_rich_final_winner_blitz"),
    ),

    # --- Tier 3 ---
    StatisticsType.REGISTER_ON_MATCH: lambda ch: GenericStatistics(
        ch,
        stat_type=StatisticsType.REGISTER_ON_MATCH,
        description_text="Зареєструйся в матч — отримай +20⚡ енергії!",
        threshold=1,
        energy=20,
        describe_template="Ви зареєструвались {progress} раз(ів).",
        button_text_template="🎁 Забрати нагороду за реєстрацію",
        reward_caption_template="🏅 Ви отримали +{energy}⚡ енергії!",
        progress_getter=_progress_getter_attr("count_register_on_match"),
    ),

    # MVP — примітка: mvp_points може бути float; поріг — float
    StatisticsType.MVP_TWO: lambda ch: GenericStatistics(
        ch,
        stat_type=StatisticsType.MVP_TWO,
        description_text="Набери 2 MVP очки — отримай +50⚡ енергії і +10💰 монет!",
        threshold=2.0,
        energy=50,
        money=10,
        describe_template="Ваш рейтинг MVP: {progress}. Ще трішки до {threshold} ⭐",
        success_template="🏆 Ви набрали {threshold} MVP очок! Натискайте «{button}» та отримуйте нагороду.",
        button_text_template="🎁 Забрати нагороду за {threshold} MVP",
        reward_caption_template="🏅 Ви отримали +{energy}⚡ та +{money}💰!",
        progress_getter=_progress_getter_attr("mvp_points"),
    ),
    StatisticsType.MVP_TWO_HALF: lambda ch: GenericStatistics(
        ch,
        stat_type=StatisticsType.MVP_TWO_HALF,
        description_text="Набери 2.5 MVP очок — отримай +70⚡ енергії і +15💰 монет!",
        threshold=2.5,
        energy=70,
        money=15,
        describe_template="Ваш рейтинг MVP: {progress}. Ще трішки до {threshold} ⭐",
        success_template="🏆 Ви набрали {threshold} MVP очок! Натискайте «{button}» та отримуйте нагороду.",
        button_text_template="🎁 Забрати нагороду за {threshold} MVP",
        reward_caption_template="🏅 Ви отримали +{energy}⚡ та +{money}💰!",
        progress_getter=_progress_getter_attr("mvp_points"),
    ),
    StatisticsType.MVP_THREE: lambda ch: GenericStatistics(
        ch,
        stat_type=StatisticsType.MVP_THREE,
        description_text="Набери 3 MVP очки — отримай +100⚡ енергії і +20💰 монет!",
        threshold=3.0,
        energy=100,
        money=20,
        describe_template="Ваш рейтинг MVP: {progress}. Ще трішки до {threshold} ⭐",
        success_template="🏆 Ви набрали {threshold} MVP очок! Натискайте «{button}» та отримуйте нагороду.",
        button_text_template="🎁 Забрати нагороду за {threshold} MVP",
        reward_caption_template="🏅 Ви отримали +{energy}⚡ та +{money}💰!",
        progress_getter=_progress_getter_attr("mvp_points"),
    ),
}


# --- автоматично генерируем "stat_done_already" словарь (чтобы не дублировать) ---
def _default_done_text(stat: StatisticsType, instance: GenericStatistics) -> str:
    # простая структура: можно расширить при необходимости
    if instance.energy and instance.money:
        return f"⭐ Ви отримали нагороду за {instance._description_text.split(' — ')[0]}: +{instance.energy}⚡ і +{instance.money}💰!"
    if instance.energy:
        return f"🔥 Ви успішно виконали завдання та отримали +{instance.energy}⚡ енергії!"
    if instance.money:
        return f"💰 Ви отримали +{instance.money} монет!"
    return "Ви вже забирали нагороду за це завдання."

# корректно сформируем словарь, но нам нужен Character чтобы передать в фабрику — сделаем более надёжно:
# просто генерируем текст по типу из конфигурации (без доступа к char)
stat_done_already = {}
for st, factory in STAT_REGISTRY.items():
    # для генерации текста вызовем фабрику с фиктивным объектом, но чтобы не создавать реальный Character,
    # сделаем безопасно: создадим минимальный faux с нужными атрибутами, если это возможно.
    # Упростим: получим описание из фабрики через временный lambda, безопаснее извлечь из фабрики.__closure__ нет гарантии,
    # поэтому сформируем нейтральные тексты по типу:
    if st in (StatisticsType.MVP_TWO, StatisticsType.MVP_TWO_HALF, StatisticsType.MVP_THREE):
        # точные формулировки для MVP (как в оригинале)
        if st == StatisticsType.MVP_TWO:
            stat_done_already[st] = "⭐ Ви набрали 2 MVP очки та отримали +50⚡ енергії і +10💰 монет!"
        elif st == StatisticsType.MVP_TWO_HALF:
            stat_done_already[st] = "⭐ Ви набрали 2.5 MVP очок та отримали +70⚡ енергії і +15💰 монет!"
        else:
            stat_done_already[st] = "⭐ Ви набрали 3 MVP очки та отримали +100⚡ енергії і +20💰 монет!"
    else:
        # более общие сообщения (опираясь на исходный набор)
        text_map = {
            StatisticsType.CONDUCT_3_TRAINING: "🔥 Ви успішно провели 3 тренування та отримали +50⚡ енергії!",
            StatisticsType.CONDUCT_5_TRAINING: "🔥 Ви успішно провели 5 тренувань та отримали +75⚡ енергії!",
            StatisticsType.CONDUCT_7_TRAINING: "🔥 Ви успішно провели 7 тренувань та отримали +100⚡ енергії!",
            StatisticsType.PLAY_BLITZ: "🎉 Ви зіграли турнір та отримали +20⚡ енергії!",
            StatisticsType.PLAY_2_BLITZ: "🎉 Ви зіграли 2 турніри та отримали +70⚡ енергії!",
            StatisticsType.GOAL_IN_MATCH: "⚽ Ви забили гол та отримали +50⚡ енергії!",
            StatisticsType.RICH_SEMI_FINAL_BLITZ: "🚀 Ви дійшли до півфіналу та отримали +50⚡ енергії!",
            StatisticsType.RICH_FINAL_WIN_BLITZ: "🏆 Ви перемогли у бліц-турнірі та отримали +100⚡ енергії!",
            StatisticsType.REGISTER_ON_MATCH: "✅ Ви зареєструвались у матчі та отримали +20⚡ енергії!",
        }
        stat_done_already[st] = text_map.get(st, "Ви вже забирали нагороду за це завдання.")

# --- Пример использования ---
# Вместо: stat[StatisticsType.CONDUCT_3_TRAINING] вы теперь используете
# instance = STAT_REGISTRY[StatisticsType.CONDUCT_3_TRAINING](character)
# then instance.describe(), instance.reward_stat(message), etc.


