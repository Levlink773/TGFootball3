from sqlalchemy import (
    Column, 
    Enum, 
    String, 
    ForeignKey, 
    Integer, 
)
from sqlalchemy.orm import relationship, Mapped
from database.model_base import Base

from .payments import Payment


class MoneyPayment(Base):
    __tablename__ = 'money_payment'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(String(100), ForeignKey('payments.order_id', ondelete="CASCADE"), nullable=False)  # nullable=False
    count_money    = Column(Integer, nullable=False)
    
    payment: Mapped["Payment"] = relationship("Payment", lazy="joined")
