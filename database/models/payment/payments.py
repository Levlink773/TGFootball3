from datetime import datetime

from sqlalchemy import (
    Column, 
    BigInteger, 
    String, 
    ForeignKey, 
    DateTime, 
    Integer, 
    Boolean,
)
from database.model_base import Base



class Payment(Base):
    __tablename__ = 'payments'
    __table_args__ = {'extend_existing': True}
    
    id                   = Column(BigInteger, primary_key=True, index=True)
    order_id             = Column(String(100), nullable=False, unique=True)
    user_id              = Column(BigInteger, ForeignKey("users.user_id"), nullable=False)
    price                = Column(Integer, nullable=False)
    
    created_time_payment = Column(DateTime, default=datetime.now, nullable=False)
    payment_time         = Column(DateTime, nullable=True)
    status               = Column(Boolean, default=False, server_default="0")