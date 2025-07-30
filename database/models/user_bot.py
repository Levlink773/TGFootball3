import datetime
from enum import Enum as EnumBase

from database.model_base import Base

from sqlalchemy import (
    Column,
    BigInteger, 
    DateTime,
    String,
    Enum,
    text
)
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, Mapped, mapped_column



class STATUS_USER_REGISTER(EnumBase):
    PRE_RIGSTER_STATUS = "PRE_RIGSTER_STATUS"
    START_REGISTER = "START_REGISTER"
    CREATER_CHARACTER = "CREATE_CHARACTER"
    SEND_NAME_CHARACTER = "SEND_NAME_CHARACTER"
    SELECT_GENDER = "SELECT_GENDER"
    SELECT_POSITION = "SELECT_POSITION"
    TERRITORY_ACADEMY = "TERRITORY_ACADEMY"
    JOIN_TO_CLUB = "JOIN_TO_CLUB"
    FIRST_TRAINING = "FIRST_TRAINING"
    TRAINING_CENTER = "TRAINING_CENTER"
    BUY_EQUIPMENT = "BUY_EQUIPMENT"
    JOIN_FIRST_MATCH = "JOIN_FIRST_MATCH"
    FORGOT_TRAINING = "FORGOT_TRAINING"
    END_TRAINING = "END_TRAINING"


class UserBot(Base):
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, unique=True, index=True)  
    user_name = Column(String(255), index=True)  
    user_full_name = Column(String(255)) 
    user_time_register = Column(DateTime, default=datetime.datetime.now)
    
    referal_user_id = Column(BigInteger, nullable=True)  
    
    characters = relationship("Character", back_populates="owner", lazy="selectin")
    clubs = relationship("Club", back_populates="owner", lazy="selectin")
    status_register: Mapped[STATUS_USER_REGISTER] = mapped_column(
        Enum(STATUS_USER_REGISTER),
        nullable=False,
        default=STATUS_USER_REGISTER.PRE_RIGSTER_STATUS,
        server_default=text("'END_TRAINING'") 
    )
    
    @property
    def end_register(self) -> bool:
        return self.status_register == STATUS_USER_REGISTER.END_TRAINING
    
    @property
    def user_name_link(self):
        return f"{'@' + self.user_name if self.user_name else self.user_full_name}" 
    
    
    @hybrid_property
    def link_to_user(self):
        return f"<a href='tg://user?id={self.user_id}'>{self.user_name_link}</a>"