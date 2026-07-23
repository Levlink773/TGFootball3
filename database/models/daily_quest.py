from sqlalchemy import BigInteger, Boolean, Column, Date, Integer, UniqueConstraint

from database.model_base import Base


class DailyQuest(Base):
    __tablename__ = "daily_quests"
    __table_args__ = (UniqueConstraint("character_id", "quest_date", name="uq_daily_quest_char_date"),)

    id = Column(BigInteger, primary_key=True, index=True)
    character_id = Column(BigInteger, index=True, nullable=False)
    quest_date = Column(Date, nullable=False)
    trainings = Column(Integer, nullable=False, default=0)
    matches = Column(Integer, nullable=False, default=0)
    wins = Column(Integer, nullable=False, default=0)
    claimed = Column(Boolean, nullable=False, default=False)
    gift_claimed = Column(Boolean, nullable=False, default=False)
