from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.model_base import Base

class BlitzTeam(Base):
    __tablename__ = 'blitz_team'
    id = Column(Integer, primary_key=True)
    name = Column(String(length=255))
    characters = relationship("BlitzCharacter", back_populates="team", cascade="all, delete-orphan")
