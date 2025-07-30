from typing import Literal
from enum import Enum

class ResultTraining(Enum):
    SUCCESS = True
    FAILURE = False
    
    
TypeCharacteristic = Literal['technique', 'kicks', 'ball_selection', 'speed', 'endurance']