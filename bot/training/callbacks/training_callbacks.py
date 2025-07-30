from aiogram.filters.callback_data import CallbackData

from training.types import Stage
from training.duel.types import PositionAngle


class NextStage(CallbackData, prefix="next_etap"):
    next_stage: Stage
    count_score: int
    end_time_health: int
    

class JoinToTraining(CallbackData, prefix="join_to_training"):
    end_time_health: int
    
class QTECallback(CallbackData, prefix="qte"):
    direction: str
    correct_direction: str
    stage: int
    timestamp: float
    end_time_health: int
    
class SelectStat(CallbackData, prefix = "select_stat"):
    stat: str
    count_stat: int
    

class SelectAngleTrainingDuel(CallbackData, prefix = "select_angle"):
    angle: PositionAngle
    end_time_health: int
    duel_id: str