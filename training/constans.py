from aiogram.types import FSInputFile
from datetime import timedelta
from .types import Stage

TIMERS_REGISTER_TRAINING = [
    "10:00",
    "13:00",
    "19:00"
] # УЧЕТ ТОГО ЧТО НАДО ЗАРЕГАТЬСЯ НА ТРЕНЮ

# TIMERS_REGISTER_TRAINING = [
#     "23:46"
# ]

TIME_TRAINING = timedelta(minutes=30) #timedelta(minutes=10)#
TIME_REGISTER_TRAINING = timedelta(minutes=30) #timedelta(minutes=1)

MAX_LIMIT_JOIN_CHARACTERS = 50

DIRECTIONS = ["↖️", "⬆️", "↗️", "⬅️", "➡️", "↙️", "⬇️", "↘️"]

QTE_STAGES = [Stage.STAGE_4, Stage.STAGE_6]
DUEL_STAGE = [Stage.STAGE_DUEL]



COUNT_QTE_STAGES = 5 #2
MAX_SCORE_QTE = 35
BASE_SCORE_QTE = MAX_SCORE_QTE / COUNT_QTE_STAGES

PENALTY_STEP = 0.3  # Шаг штрафа в секундах
PENALTY_VALUE = 2  # Штраф за каждую задержку
MIN_SCORE = 2  # Минимальный балл


STAT_RANGES = {
    range(111, 151): 4,
    range(71, 111): 3,
    range(41, 71): 2,
    range(0, 41): 1
}
ENERGY_RANGES = {
    range(111, 150): 50,
    range(71, 111): 40,
    range(41, 71): 30,
    range(0, 41): 20
}

#=======================PVP_CONSTANS=============================#
MAX_SCORE_PVP_DUEL = 50
PERIOD_STAGE = 2
if PERIOD_STAGE // 2 == 0:
    raise "PERIOD_STAGE ДОЛЖНО БЫТЬ КРАТНО 2"

PERIOD_STAGE_FIGHT_DUEL = 3 #1
TIMES_SLEEP_ENTRY_DATA_DUEL = 15
SCORE_WINNER_DUEL_STAGE = int(MAX_SCORE_PVP_DUEL/PERIOD_STAGE/PERIOD_STAGE_FIGHT_DUEL)


FORWARD_LOSS_GOAL       = FSInputFile("src/training/duel/forward_loss.jpg")
GOALKEPEER_LOSS_GOAL    = FSInputFile("src/training/duel/goalkepper_loss_goal.jpg")

FORWARD_GOAL            = FSInputFile("src/training/duel/forward_goal.jpg")
GOALKEPEER_GOAL         = FSInputFile("src/training/duel/goal_goalkepeer.jpg")

PHOTO_GOALKEEPER        = FSInputFile("src/training/duel/PHOTO_GOALKEPPER.jpg")
PHOTO_FORWARD           = FSInputFile("src/training/duel/PHOTO_FORWARD.jpg")

#==============================PVP_DUEL_CONSTANS=============================#
