from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import (
    Column,
    BigInteger, 
    DateTime,
    ForeignKey,
    text,
    Integer,
    Enum,
    func
)
from database.model_base import Base
from training.types import Stage

class TrainingTimer(Base):
    __tablename__ = 'training_timer'
    
    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    time_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)


class CharacterJoinTraining(Base):
    __tablename__ = 'character_join_training'

    id : Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True
    )
    character_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('characters.id'), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey('users.user_id')
    )
    time_join: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now())
    scores: Mapped[int] = mapped_column(
        Integer, nullable=False, default = 0, server_default=text('0')
    )
    stage: Mapped[Stage] = mapped_column(
        Enum(Stage), nullable=False, default = Stage.STAGE_1, server_default=text("'STAGE_1'")
    )
    training_is_end: Mapped[bool] = mapped_column(
        Integer, nullable=False, default = 0, server_default=text('0')
    )
    