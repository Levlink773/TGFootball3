from sqlalchemy import Column, BigInteger, String, ForeignKey, Float, Integer

from database.model_base import Base



class MatchCharacter(Base):
    __tablename__ = 'match_character'
    
    id = Column(BigInteger, primary_key=True, index=True)
    
    character_id = Column(BigInteger, ForeignKey('characters.id', ondelete="CASCADE"))
    match_id     = Column(String(255), ForeignKey('league_fight.match_id', ondelete="CASCADE"), nullable=False)
    group_id     = Column(String(255), nullable=False)
    
    club_id      = Column(Integer, nullable=False)
    goals_count  = Column(Integer, nullable=False, default=0, server_default='0')
    count_score  = Column(Float, nullable=False, default=0, server_default='0')