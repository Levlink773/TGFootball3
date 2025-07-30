from datetime import datetime

from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey, text, Integer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, Mapped
from database.models.character import Character

from config import LEAGUES
from database.model_base import Base

from typing import Union


class Duel(Base):
    __tablename__ = 'duels'
    id = Column(BigInteger, primary_key=True, index=True)
    
    duel_id = Column(String(255), nullable=False)
    
    user_1_id = Column(BigInteger, ForeignKey('characters.id'))  
    user_1:Mapped["Character"]   = relationship("Character", foreign_keys=[user_1_id], lazy="selectin")
    
    user_2_id = Column(BigInteger, ForeignKey('characters.id'))  
    user_2:Mapped["Character"]   = relationship("Character", foreign_keys=[user_2_id], lazy="selectin")
    
    point_user_1 =  Column(Integer, default=0, server_default="0", insert_default=0, nullable=False)
    point_user_2 = Column(Integer, default=0, server_default="0", insert_default=0, nullable=False)
    
    bit_user_1   = Column(Integer, default=0, server_default="0", insert_default=0, nullable=False)
    bit_user_2   = Column(Integer, default=0, server_default="0", insert_default=0, nullable=False)
    
    created_time = Column(DateTime, default=datetime.now, nullable=False)
    
    @property
    def get_winner_duel(self) -> Union[Character, list[Character]]:
        if self.point_user_1 == self.point_user_2:
            return [self.user_1, self.user_2]
        
        return self.user_1 if self.point_user_1 > self.point_user_2 else self.user_2