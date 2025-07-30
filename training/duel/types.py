import random

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from uuid import uuid4

class RoleDuel(Enum):
    GOALKEEPER = "GOALKEEPER"
    FORWARD = "FORWARD"

    def toggle(self) -> "RoleDuel":
        return RoleDuel.FORWARD if self == RoleDuel.GOALKEEPER else RoleDuel.GOALKEEPER

    @staticmethod
    def get_random_role() -> "RoleDuel":
        return random.choice([RoleDuel.FORWARD, RoleDuel.GOALKEEPER])
    

class PositionAngle(Enum):
    UP = "UP"
    LEFT = "LEFT"
    RIGHT = "RIGHT"

class DuelUser(BaseModel):
    
    user_id: int
    points: int = Field(ge=0, default=0)
    pvp_role: RoleDuel
    
    position_angle: Optional[PositionAngle] = None
    is_bot: bool = False

    def nullify_angle(self) -> None:
        self.position_angle = None
    
    def change_role(self) -> RoleDuel:
        self.pvp_role = self.pvp_role.toggle()
        return self.pvp_role
        
    def add_points(self, points: int) -> None:
        self.points += points
    
    def select_random_angle(self) -> None:
        self.position_angle = random.choice([PositionAngle.UP, PositionAngle.LEFT, PositionAngle.RIGHT])
    

class DuelData(BaseModel):
    duel_id: str = Field(default_factory=lambda: str(uuid4())[:10])
    
    user_1: DuelUser
    user_2: DuelUser
    
    def change_roles_character(self) -> None:
        self.user_1.pvp_role,self.user_2.pvp_role = self.user_2.pvp_role,self.user_1.pvp_role

    def get_opponent(self, user_id: int) -> DuelUser:
        if user_id == self.user_1.user_id:
            return self.user_2
        else:
            return self.user_1
        
    def get_user_by_role(self, role: RoleDuel) -> DuelUser:
        if self.user_1.pvp_role == role:
            return self.user_1
        else:
            return self.user_2
    
    def get_user_by_id(self, user_id: int) -> DuelUser:
        if self.user_1.user_id == user_id:
            return self.user_1
        else:
            return self.user_2
    
        
    def anulate_angle_users(self) -> None:
        self.user_1.nullify_angle()
        self.user_2.nullify_angle()
        
    def add_points_to_role(self, role: RoleDuel, points: int):
        if self.user_1.pvp_role == role:
            self.user_1.add_points(points)
        else:
            self.user_2.add_points(points)
            
    def is_same_angle(self) -> bool:
        return self.angle_user_1 == self.angle_user_2
            
    @property
    def goalkepper(self) -> DuelUser:
        if self.user_1.pvp_role == RoleDuel.GOALKEEPER:
            return self.user_1
        else:
            return self.user_2
    
    @property
    def forward(self) -> DuelUser:
        if self.user_1.pvp_role == RoleDuel.FORWARD:
            return self.user_1
        else:
            return self.user_2
        
    @property
    def all_users(self) -> list[DuelUser]:
        return [self.user_1, self.user_2]