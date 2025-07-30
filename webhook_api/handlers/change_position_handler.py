from aiogram import Bot
from aiohttp.web import Response
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from webhook_api.schemas import MonoResultSchema
from ..base_endpoint import EndPoint, HTTPMethod

from database.models.payment.change_position_payment import ChangePositionPayment

from services.payment_service import PaymentServise
from services.character_service import CharacterService
from config import BOT_TOKEN

class MonoResultChangePosition(EndPoint):
    schema = MonoResultSchema
    data: MonoResultSchema
    method = HTTPMethod.POST
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    TEXT_TEMPLATE = """
<b>Вітаємо! 🎉</b>

Твій футболіст успішно змінив позицію!⚽
Твоя нова позиція - <u><b>{new_position_name}</b></u>  
Тепер він готовий до нових викликів на полі. Пам’ятай:  
🚨 <b>Характеристики персонажа було оновлено</b>.  
На новій позиції твоя бойова сила залежатиме від інших коефіцієнтів, які ідеально підходять для обраної ролі.  

Дякуємо за вибір нашого сервісу! Бажаємо успіху та неймовірних досягнень на полі! 💪🏆
"""
    
    async def handle_request(self) -> Response:
        payment: ChangePositionPayment = await PaymentServise.get_payment(
            order_id=self.data.invoiceId,
            type_payment = ChangePositionPayment
        )
        
        if not payment:
            return
        
        if self.data.status != "success":
            return
        
        if payment.payment.status:
            return
        
        character = await CharacterService.get_character(payment.payment.user_id)
        await CharacterService.change_position(
            character_id = character.id,
            position = payment.position.value
        )

        await self.bot.send_message(
            chat_id = payment.payment.user_id,
            text    = self.TEXT_TEMPLATE.format(
                new_position_name = payment.position.value)
        )
        await PaymentServise.change_payment_status(order_id=self.data.invoiceId)
        return self.OK()


