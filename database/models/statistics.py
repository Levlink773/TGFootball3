from sqlalchemy import Column, BigInteger, ForeignKey, Enum
from sqlalchemy.orm import relationship

from database.model_base import Base
from stats.stat_enum import StatisticsType


class Statistics(Base):
    __tablename__ = 'stats'
    id = Column(BigInteger, primary_key=True)
    character_id = Column(BigInteger, ForeignKey('characters.id'), nullable=False)
    stat_type = Column(Enum(StatisticsType), nullable=False)
    character = relationship("Character", back_populates="statistics", lazy="selectin")