from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from database.model_base import Base

class BlitzTeam(Base):
    __tablename__ = 'blitz_team'
    id = Column(Integer, primary_key=True)

    characters = relationship("BlitzCharacter", back_populates="team", cascade="all, delete-orphan")
