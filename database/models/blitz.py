from datetime import datetime

from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import relationship
from database.model_base import Base

class Blitz(Base):
    __tablename__ = 'blitzs'
    id = Column(Integer, primary_key=True)
    start_at = Column(DateTime, default=datetime.now)

    characters = relationship("BlitzCharacter", back_populates="blitz", cascade="all, delete-orphan")

    @property
    def can_register(self) -> bool:
        now = datetime.now()
        return now < self.start_at