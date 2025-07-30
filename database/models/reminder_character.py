from datetime import datetime, timedelta

from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey, text, Integer
from sqlalchemy.orm import relationship, Mapped

from database.model_base import Base


class ReminderCharacter(Base):
    __tablename__ = 'reminder_characters'
    
    id = Column(BigInteger, primary_key=True, index=True)
    
    character_id = Column(BigInteger, ForeignKey('characters.id', ondelete="CASCADE"), unique=True)

    character_in_training = Column(Boolean, default=False)
    character_in_duel     = Column(Boolean, default=False, server_default="0")
    
    training_stats        = Column(String(255), nullable=True)
    time_start_training   = Column(DateTime, nullable=True)
    time_training_seconds = Column(BigInteger, nullable=True)  
    
    education_reward_date = Column(DateTime, default=datetime(1970, 1, 1), server_default=text('\'1970-01-01 00:00:00\''), nullable=False)
    time_to_join_club     = Column(DateTime, default=datetime(1970, 1, 1), server_default=text('\'1970-01-01 00:00:00\''), nullable=False)

    character = relationship("Character", back_populates="reminder", uselist=False)

    @property
    def time_training(self) -> timedelta | None:
        if self.time_training_seconds is None:
            return None
        return timedelta(seconds=self.time_training_seconds)
    
    @property
    def end_time_training(self) -> datetime | None:
        if (self.time_training_seconds is None) or (self.time_start_training is None):
            return None 
        
        return self.time_start_training + self.time_training
    
    @property
    def time_left_training(self) -> timedelta | None:
        if (self.time_training_seconds is None) or (self.time_start_training is None):
            return None
        
        return datetime.now() - self.end_time_training 