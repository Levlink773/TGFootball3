from enum import Enum as PyEnum

from aiogram.types import FSInputFile
from apscheduler.triggers.cron import CronTrigger

from database.models.character import Character
from database.models.item import Item

from datetime import datetime, timedelta

from config import PositionCharacter, Gender
import random


    
class ItemCategory(PyEnum):
    T_SHIRT = "T-shirt"
    SHORTS = "Shorts"
    GAITERS = "Gaiters"
    BOOTS = "Boots"
    



chance_add_point = {
    timedelta(minutes = 2)   : 60,
    timedelta(seconds = 5)   : 90,
    timedelta(minutes = 5)   : 100, #ПЕРВАЯ ТРЕНИРОВКА
    timedelta(minutes = 30)  : 35,
    timedelta(minutes = 60)  : 45,
    timedelta(minutes = 90)  : 55,
    timedelta(minutes = 120) : 75,
}

CHANCE_VIP_PASS = 5

const_energy_by_time = {
    timedelta(seconds = 5)   : 5,
    timedelta(minutes = 2)   : 20,
    timedelta(minutes = 30)  : 10,
    timedelta(minutes = 60)  : 20,
    timedelta(minutes = 90)  : 40,
    timedelta(minutes = 120) : 60,
}


const_name_characteristics = {
    "technique"        : "🎯 Техніка",
    "kicks"            : "🥋 Удари",
    "ball_selection"   : "🛡️ Відбір м’яча",
    "speed"            : "⚡ Швидкість",
    "endurance"        : "🏃 Витривалість"
}

photos = {
    (Gender.MAN, PositionCharacter.MIDFIELDER): 'src/photo_character/man_midfielder.jpg',
    (Gender.WOMAN, PositionCharacter.MIDFIELDER): 'src/photo_character/woman_midfielder.jpg',
    (Gender.MAN, PositionCharacter.DEFENDER): 'src/photo_character/man_defender.jpg',
    (Gender.WOMAN, PositionCharacter.DEFENDER): 'src/photo_character/woman_defender.jpg',
    (Gender.MAN, PositionCharacter.GOALKEEPER): 'src/photo_character/man_goalkeeper.jpg',
    (Gender.WOMAN, PositionCharacter.GOALKEEPER): 'src/photo_character/woman_goalkeeper.jpg',
    (Gender.MAN, PositionCharacter.ATTACKER): 'src/photo_character/man_attacker.jpg',
    (Gender.WOMAN, PositionCharacter.ATTACKER): 'src/photo_character/woman_attacker.jpg',
}



def get_photo_character(character: Character) -> FSInputFile:
    return FSInputFile(photos.get((character.gender_enum, character.position_enum), 'path/to/default_photo.jpg'))

GYM_PHOTO        = FSInputFile("src/gym_photo.jpg")
CLUB_PHOTO       = FSInputFile("src/club_photo.jpg")
CHARACTER_SEND_OFFER_JOIN_TO_CLUB = FSInputFile("src/character_send_offer_join_to_club.png")
FIGHT_MENU       = FSInputFile("src/fight_club_menu.jpg")
JOIN_TO_FIGHT    = FSInputFile("src/join_to_fight.jpg")
LEAGUE_PHOTO     = FSInputFile("src/league_photo.jpg")
PLOSHA_PEREMOGU  = FSInputFile("src/plosha_peremogu.jpg") 
EDUCATION_CENTER = FSInputFile("src/education_center_photo.jpg")
HALL_FAME_PHOTO  = FSInputFile("src/hall_fame_photo.jpg")
DUEL_PHOTO       = FSInputFile("src/duel_photo.jpg")
CHRISTMAS_TREE_PHOTO = FSInputFile("src/сhristmas_tree.jpg")
MAGAZINE_PHOTO   = FSInputFile("src/magazine_photo.jpg")
BOXES_PHOTO      = FSInputFile("src/boxes_photo.jpg")
DEFAULT_MAGAZINE_PHOTO = FSInputFile("src/default_store.jpg")
LUXE_STORE_PHOTO = FSInputFile("src/luxe_store.jpg")
ENERGY_STORE_PHOTO = FSInputFile("src/energy_store.jpg")
VIP_PASS_PHOTO   = FSInputFile("src/vip_pass_photo.jpg")
BANK_PHOTO       = FSInputFile("src/bank_photo.jpg")
CHANGE_POSITION_PHOTO = FSInputFile("src/change_position_photo.jpg")
END_VIP_PASS_PHOTO = FSInputFile("src/end_vip_pass_photo.jpg")
LOW_ENERGY_PHOTO = FSInputFile("src/low_energy_photo.jpg")
BUY_TRAINING_KEY = FSInputFile("src/buy_key_training.jpg")
NEED_TRAINING_KEY = FSInputFile("src/need_training_key.jpg")
HALL_FAME_POSITION_PHOTO = FSInputFile("src/hall_fame_position_photo.jpg")
PHOTO_NEW_BONUS_MEMBER_HAR = FSInputFile("src/new_member_bonus_har.png")
PHOTO_MENU_MATCHES = FSInputFile("src/menu_matches.jpg")

MAX_LEN_MEMBERS_CLUB = 11

# TIME_FIGHT = timedelta(minutes=2)
TIME_FIGHT = timedelta(minutes=20)
BUFFER_TIME = timedelta(minutes=3)

TIME_RESET_ENERGY_CLUB = CronTrigger(hour=22, minute=10)
TIME_RESET_ENERGY_CHARACTER = CronTrigger(hour=22, minute=15)


DELTA_TIME_EDUCATION_REWARD = timedelta(hours=12)

HOURS_END_TIME = 22

KOEF_ENERGY_DONATE = 2

PROCENT_TO_SELL = 30

REFERAL_EXP = 20
ALL_COUNT_ENERGY_BIT = [30,50,100,150]



TIME_TO_JOIN_TO_CLUB = timedelta(minutes=2)

#KEY - COUNT ENERGY | VALUE - PRICE UAH
count_energys = [5,10,20,50,70]
CONST_PRICE_ENERGY = {
    100  : 100,
    150  : 150,
    300  : 270,
    600  : 490,
    900  : 670
}

START_DAY_DEFAULT_LEAGUE = 1

DUEL_START_DAY_SEASON = 21
DUEL_END_DAY_SEASON   = 28

X2_REWARD_WEEKEND_START_DAY = 21
X2_REWARD_WEEKEND_END_DAY   = 28

START_DAY_BEST_LEAGUE = 21
END_DAY_BEST_LEAGUE = 30

START_DAY_BEST_20_CLUB_LEAGUE = 3
END_DAY_BEST_20_CLUB_LEAGUE = 21

END_MATCH_TOP_20_CLUB = CronTrigger(day = END_DAY_BEST_20_CLUB_LEAGUE,hour=8)

SEND_GONGRATULATION_END_BEST_MATCH = CronTrigger(
    day = END_DAY_BEST_20_CLUB_LEAGUE,
    hour=19,
    minute=30
)


ITEM_PER_PAGE = 9

def GET_RANDOM_NUMBER(LIMIT_1 = 1, LIMIT_2 = 5):
    return random.randint(LIMIT_1,LIMIT_2)




#CHRISTMAS
def date_is_get_reward_christmas_tree() -> bool:
    today = datetime.now().date()
    today_month_day = (today.month, today.day)
    start_date = (12, 28)
    end_date = (1, 10)
    return start_date <= today_month_day or today_month_day <= end_date

MIN_ENERGY_CHRISTMAS_REWARD = 10
MAX_ENERGY_CHRISTMAS_REWARD = 50

MIN_MONEY_CHRISTMAS_REWARD = 5
MAX_MONEY_CHRISTMAS_REWARD = 10

#======================================================


lootboxes = {
    "small_box": {
        "name_lootbox": "Маленький бокс футболіста",
        "min_energy": 50,
        "max_energy": 100,
        "min_money": 5,
        "max_money": 15,
        "min_exp": 1,
        "max_exp": 5,
        "price": 75
    },
    "medium_box": {
        "name_lootbox": "Середній бокс футболіста",
        "min_energy": 100,
        "max_energy": 200,
        "min_money": 15,
        "max_money": 30,
        "min_exp": 5,
        "max_exp": 10,
        "price": 145
    },
    "large_box": {
        "name_lootbox": "Преміум бокс",
        "min_energy": 250,
        "max_energy": 400,
        "min_money": 30,
        "max_money": 50,
        "min_exp": 10,
        "max_exp": 15,
        "price": 245
    },
    "new_member_box" : {
        "name_lootbox": "Бокс новачка",
        "min_energy": 100,
        "max_energy": 200,
        "min_money": 20,
        "max_money": 40,
        "min_exp": 5,
        "max_exp": 10,
        "price": None
    },
}

PRICE_CHANGE_POSITION = 150
PRICE_TRAINING_KEY = 49

TOTAL_POINTS_ADD_NEW_MEMBER = 300