import os

from enum import Enum
from urllib.parse import quote

from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DB_HOST     = quote(os.getenv("DB_HOST"))
DB_PASSWORD = quote(os.getenv("DB_PASSWORD"))
DB_LOGIN    = quote(os.getenv("DB_LOGIN"))
DB_NAME     = quote(os.getenv("DB_NAME"))
DB_PORT     = quote(os.getenv("DB_PORT"))

TOKEN_MONOBANK = os.getenv("TOKEN_MONOBANK")

CALLBACK_URL_WEBHOOK_ENERGY   = os.getenv("CALLBACK_URL_WEBHOOK_ENERGY")
CALLBACK_URL_WEBHOOK_BOX      = os.getenv("CALLBACK_URL_WEBHOOK_BOX")
CALLBACK_URL_WEBHOOK_VIP_PASS = os.getenv("CALLBACK_URL_WEBHOOK_VIP_PASS") 
CALLBACK_URL_WEBHOOK_MONEY    = os.getenv("CALLBACK_URL_WEBHOOK_MONEY")
CALLBACK_URL_WEBHOOK_CHANGE_POSITION = os.getenv("CALLBACK_URL_WEBHOOK_CHANGE_POSITION")
CALLBACK_URL_WEBHOOK_BUY_TRAINING_KEY = os.getenv("CALLBACK_URL_WEBHOOK_BUY_TRAINING_KEY")

MAIN_CHAT_GROUP_ID = os.getenv("MAIN_CHAT_GROUP_ID")

WEBAPP_HOST = os.getenv("WEBAPP_HOST")
WEBAPP_PORT = os.getenv("WEBAPP_PORT")

VIDEO_ID    = os.getenv("VIDEO_ID")


BOT_TOKEN = os.getenv("BOT_TOKEN")

LINK_TO_CHAT = os.getenv("LINK_TO_CHAT")

CONST_ENERGY = 150
CONST_VIP_ENERGY = 300

EPOCH_ZERO = datetime(1970, 1, 1)

ADMINS = [7477142926] # [6790393255, 577395732] CHANGE BACK

class DatabaseType(Enum):
    USER = 'bot'


class DatabaseConfig:
    _configs = {
        DatabaseType.USER: f"mysql+aiomysql://{DB_LOGIN}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    }

    @classmethod
    def get_connection_string(cls, db_type: DatabaseType) -> str:
        return cls._configs.get(db_type)

class Gender(Enum):
    MAN   = "Чоловік"
    WOMAN = "Жінка"
    
class PositionCharacter(Enum):
    MIDFIELDER = "Півзахисник"
    DEFENDER   = "Захисник"
    GOALKEEPER = "Воротар"
    ATTACKER   = "Нападник" 
    
POSITION_COEFFICIENTS = {
    PositionCharacter.DEFENDER: {
        'ball_selection': 1.35,
        'endurance': 1.35,
        'speed': 1.2,
    },
    PositionCharacter.GOALKEEPER: {
        'speed': 1.5,
        'kicks': 1.3,
        'ball_selection': 1.2,
    },
    PositionCharacter.MIDFIELDER: {
        'technique': 1.35,
        'speed': 1.4,
        'ball_selection': 1.2,
    },
    PositionCharacter.ATTACKER: {
        'kicks': 1.4,
        'technique': 1.2,
        'speed': 1.1,
    }
}
    

POSITION_DECLENSIONS = {
    PositionCharacter.MIDFIELDER: {
        Gender.MAN: "Півзахисник",
        Gender.WOMAN: "Півзахисниця"
    },
    PositionCharacter.DEFENDER: {
        Gender.MAN: "Захисник",
        Gender.WOMAN: "Захисниця"
    },
    PositionCharacter.GOALKEEPER: {
        Gender.MAN: "Воротар",
        Gender.WOMAN: "Воротарка"
    },
    PositionCharacter.ATTACKER: {
        Gender.MAN: "Нападник",
        Gender.WOMAN: "Нападниця"
    }
}
        
    
LEAGUES = [
    "🟢 Ліга новачків",
    "🔰 Ліга любителів",
    "⚪ Ліга аматорів",
    "🔶 Ліга напівпрофесіоналів",
    "🏅 Професійна ліга",
    "⚽ Друга ліга",
    "⚜️ Перша ліга",
    "🏆 Вища ліга",
    "🥇 Прем'єр-ліга"
]


INSTRUCTION = [
    "👋Вітаємо тебе у TG Football - перший симулятор життя футболіста в телеграм! ⚽️Ходімо розповім тобі про самі основні функціі гри, це займе 1 хвилину.",
    "🏋️‍♂️Тренажерний зал - місце тренувань твого гравця, саме там ти можеш прокачати його «скіли» та покращити характеристики. 💪",
    "🏫 Навчальний центр - Тут кожні 12 годин на тебе чекає новий шанс! Заходь в навчальний центр, щоб отримати досвід і заробити монети для свого персонажа. Поліпшуй свої навички, заробляй більше, ставай легендою на полі.",
    "🏟️Стадіон - сама головна локація гри, розклад ігор, результати, таблиця…\nМатч відбувається кожного дня з 1 по 19 число кожного місяця о 21:00, але не забудь зареєструватися на найближчий матч, ти маєш прийти на нього.",
    "Створюй команду або приєднуйся до вже існуючих команд  в меню 🎪«Моя команда»  - важливо знати, якщо зараз 1-20 число місяця то краще обрати існуючу команду, реєстрація команд в нові ліги відбувається з 20 по 31 число кожного місяця.",
    f'🏆 Розпочинай шлях футболіста!\n🧤 Ходи в тренажерний зал та розпочни своє перше тренування!\n📇 Додавайся в існуючу команду або створюй свій'
    ]