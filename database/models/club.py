from aiogram.types import FSInputFile
from datetime import datetime

from sqlalchemy import Column, BigInteger, String, DateTime, Boolean, ForeignKey, text, Integer
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, Mapped
from database.models.character import Character

from config import LEAGUES
from database.model_base import Base

class Club(Base):
    __tablename__ = 'clubs'
    
    id             = Column(BigInteger, primary_key=True, index=True)
    name_club      = Column(String(100), nullable=False)
    owner_id       = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    link_to_chat   = Column(String(255), nullable=True)
    league         = Column(String(254), nullable=False, default=LEAGUES[0])
    is_fake_club   = Column(Boolean, default=False)
    description    = Column(String(255), nullable=True, default="Не вказано", server_default="Не вказано")
    
    schema         = Column(String(255), nullable=False, default="sсhema_1", server_default="sсhema_1")
    time_edit_schema = Column(DateTime, default=datetime(1970, 1, 1), server_default=text('\'1970-01-01 00:00:00\''), nullable=False)
    
    energy_applied = Column(Integer, default=0, server_default='0')
    
    custom_url_photo_stadion = Column(String(255), nullable = False, default = "src/fight_club_menu.jpg", server_default= "src/fight_club_menu.jpg")
    custom_name_stadion  = Column(String(255), nullable = False, default = "Стадіон", server_default= "Стадіон")
    is_invite_only = Column(Boolean, default=False, server_default='0')
    
    owner          = relationship("UserBot", back_populates="clubs", lazy="subquery")
    characters:Mapped[list['Character']]  = relationship("Character", back_populates="club", lazy="subquery")

    @hybrid_property
    def total_power(self) -> int:
        return sum(character.full_power for character in self.characters)

    @hybrid_property
    def koef_energy(self) -> float:
        if self.energy_applied >= 500:
            return 1.3
        elif self.energy_applied >= 400:
            return 1.25
        elif self.energy_applied >= 300:
            return 1.2
        elif self.energy_applied >= 200:
            return 1.15
        elif self.energy_applied >= 100:
            return 1.1
        else:
            return 1.0
    
    @property
    def custom_photo_stadion(self) -> FSInputFile:
        return FSInputFile(
            path = self.custom_url_photo_stadion
        )