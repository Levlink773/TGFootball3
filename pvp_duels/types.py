from dataclasses import dataclass

from database.models.character import Character
from enum import Enum

class RoleDuel(Enum):
    GOALKEEPER = "goalkeeper"
    FORWARD = "forward"


class PositionAngle(Enum):
    UP = "up"
    LEFT = "left"
    RIGHT = "right"



@dataclass
class DuelUser:
    duel_id: str
    
    user_1: Character 
    user_2: Character 
    
    points_user_1: int = 0
    points_user_2: int = 0
    
    role_user_1: RoleDuel = None
    role_user_2: RoleDuel = None
    
    position_angle_user_1: PositionAngle | None = None
    position_angle_user_2: PositionAngle | None = None
    
    bid_user_1:int = None 
    bid_user_2:int = None
    
    
    @property
    def all_users_duel(self) -> list[Character]:
        return [self.user_1, self.user_2]

    def get_opponent(self, my_user: Character) -> Character:
        if my_user.id == self.user_1.id:
            return self.user_2
        elif my_user.id == self.user_2.id:
            return self.user_1
    
    def change_roles_character(self) -> None:
        self.role_user_1,self.role_user_2 = self.role_user_2,self.role_user_1
    
    def anulate_angle_users(self) -> None:
        self.position_angle_user_1, self.position_angle_user_2 = None, None 
    
    def get_user_by_role(self, role: RoleDuel) -> Character:
        return self.user_1 if self.role_user_1 == role else self.user_2
    
    def get_role_by_user(self, character: Character) -> RoleDuel:
        return self.role_user_1 if self.user_1.id == character.id else self.role_user_2
    
    def add_points_to_role(self, role: RoleDuel, points: int):
        if self.role_user_1 == role:
            self.points_user_1 += points
        else:
            self.points_user_2 += points
            