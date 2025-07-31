from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from database.model_base import Base

class BlitzCharacter(Base):
    __tablename__ = 'blitz_character'
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(Integer, ForeignKey('character.id'))

    blitz_id = Column(Integer, ForeignKey("blitzs.id", ondelete="CASCADE"))
    team_id = Column(Integer, ForeignKey("blitz_team.id", ondelete="CASCADE"))

    blitz = relationship("Blitz", back_populates="characters")
    team = relationship("BlitzTeam", back_populates="characters")
