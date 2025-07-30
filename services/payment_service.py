from typing import Union
from sqlalchemy import select, update

from database.models.payment.payments import Payment
from bot.routers.stores.vip_pass.types import VipPassTypes
from database.models.payment.vip_pass_payment import VipPassPayment
from database.models.payment.box_payment import BoxPayment, TypeBox
from database.models.payment.money_payment import MoneyPayment
from database.models.payment.energy_payment import EnergyPayment
from database.models.payment.change_position_payment import ChangePositionPayment
from database.models.payment.key_payment import KeyPayment

from database.session import get_session

from config import PositionCharacter

from logging_config import logger
from typing import Any


class PaymentServise:
    @classmethod
    async def create_payment(
        cls, 
        price: int, 
        user_id: int, 
        order_id: str,
    ) -> Payment:
        async for session in get_session():
            async with session as sess:  
                try:
                    new_payment  = Payment(
                        order_id      = order_id,
                        user_id       = user_id,
                        price         = price,
                    )
                    sess.add(new_payment)
                    await sess.commit()
                    return new_payment
                except Exception as E:
                    logger.error(f"err create payment: {E}")
                    
    
    @classmethod
    async def get_payment(cls, order_id: str, type_payment: Any) -> Any:
        async for session in get_session():
            async with session as sess:
                try:    
                    stmt = select(type_payment).where(type_payment.order_id == order_id)
                    result = await session.execute(stmt)
                    return result.scalar_one_or_none()
                except Exception as E:
                    logger.error(f"err get payment: {E}")
                    
    @classmethod
    async def change_payment_status(cls, order_id: str):
        async for session in get_session():
            async with session as sess:
                try:    
                    stmt = update(Payment).where(Payment.order_id == order_id).values(status=True)
                    await sess.execute(stmt)
                    await sess.commit()
                except Exception as E:
                    logger.error(f"err change payment status: {E}")
                    
                    
    @classmethod
    async def create_vip_pass_payment(
        cls,
        order_id: str,
        type_vip_pass: VipPassTypes
    ):
        async for session in get_session():
            async with session as sess:
                try:
                    new_payment  = VipPassPayment(
                        order_id      = order_id,
                        type_vip_pass = type_vip_pass
                    )
                    sess.add(new_payment)
                    await sess.commit()
                    return new_payment
                except Exception as E:
                    logger.error(f"err create vip pass payment: {E}")
                    
    @classmethod
    async def create_money_payment(
        cls,
        order_id: str,
        count_money: int
    ):
        async for session in get_session():
            async with session as sess:
                try:
                    new_payment  = MoneyPayment(
                        order_id      = order_id,
                        count_money = count_money
                    )
                    sess.add(new_payment)
                    await sess.commit()
                    return new_payment
                except Exception as E:
                    logger.error(f"err create vip pass payment: {E}")
                    
    @classmethod
    async def create_box_payment(
        cls,
        order_id: str,
        type_box: TypeBox
    ):
        async for session in get_session():
            async with session as sess:
                try:
                    new_payment  = BoxPayment(
                        order_id = order_id,
                        type_box = type_box
                    )
                    sess.add(new_payment)
                    await sess.commit()
                    return new_payment
                except Exception as E:
                    logger.error(f"err create vip pass payment: {E}")
                    
    @classmethod
    async def create_energy_payment(
        cls,
        order_id: str,
        amount_energy: int
    ):
        async for session in get_session():
            async with session as sess:
                try:
                    new_payment  = EnergyPayment(
                        order_id = order_id,
                        amount_energy = amount_energy
                    )
                    sess.add(new_payment)
                    await sess.commit()
                    return new_payment
                except Exception as E:
                    logger.error(f"err create vip pass payment: {E}")
                    
    @classmethod
    async def create_change_position_payment(
        cls,
        order_id: str,
        position: PositionCharacter
    ):
        async for session in get_session():
            async with session as sess:
                try:
                    new_payment  = ChangePositionPayment(
                        order_id = order_id,
                        position = position
                    )
                    sess.add(new_payment)
                    await sess.commit()
                    return new_payment
                except Exception as E:
                    logger.error(f"err create vip pass payment: {E}")
    
    @classmethod
    async def create_buy_training_key_payment(
        cls,
        order_id: str
    ):
        async for session in get_session():
            async with session as sess:
                try:
                    new_payment  = KeyPayment(
                        order_id = order_id,
                    )
                    sess.add(new_payment)
                    await sess.commit()
                    return new_payment
                except Exception as E:
                    logger.error(f"err create vip pass payment: {E}")