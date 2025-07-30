from datetime import datetime, timedelta

from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, Integer, Boolean, text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, Mapped

from config import PositionCharacter, Gender, CONST_ENERGY, POSITION_DECLENSIONS, POSITION_COEFFICIENTS
from database.models.reminder_character import ReminderCharacter



from database.model_base import Base


class ChristmasReward(Base):
    __tablename__ = 'christmas_reward'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id  = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    time_get = Column(DateTime, nullable=True)

    @property
    def get_next_reward(self) -> datetime:
        return self.time_get + timedelta(days=1)
    
    @property
    def can_be_rewarded(self) -> bool:
        if self.time_get is None:
            return True
        return datetime.now() >= self.get_next_reward