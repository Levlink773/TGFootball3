from enum import Enum


class TypeGoalEvent(Enum):
    GOAL = "GOAL"
    NO_GOAL = "NO_GOAL"
    PING_DONATE_ENERGY = "PING_DONATE_ENERGY"
    

class GoalEvent:
    GOAL_SCORED = "GOAL_SCORED"
    GOAL_CONCEDED = "GOAL_CONCEDED"