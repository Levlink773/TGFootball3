import random

from pvp_duels.types import PositionAngle, RoleDuel

def select_random_roles() -> list[RoleDuel]:
    if random.choice([True, False]):
        return RoleDuel.FORWARD, RoleDuel.GOALKEEPER
    else:
        return RoleDuel.GOALKEEPER, RoleDuel.FORWARD

def select_random_angle() -> PositionAngle:
    return random.choice( [PositionAngle.LEFT, PositionAngle.RIGHT, PositionAngle.UP] )