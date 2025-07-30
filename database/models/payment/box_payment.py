from sqlalchemy import (
    Column, 
    Enum, 
    String, 
    ForeignKey, 
    Integer, 
)
from sqlalchemy.orm import relationship, Mapped

from database.model_base import Base
from database.models.types import TypeBox

from .payments import Payment


class BoxPayment(Base):
    __tablename__ = 'box_payment'
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)

    order_id = Column(String(100), ForeignKey('payments.order_id', ondelete="CASCADE"), nullable=False)  # nullable=False
    type_box:Mapped[TypeBox] = Column(Enum(TypeBox), nullable=True)

    payment: Mapped["Payment"] = relationship("Payment", lazy="joined")
