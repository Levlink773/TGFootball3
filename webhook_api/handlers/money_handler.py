from aiogram import Bot
from aiohttp.web import Response
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from webhook_api.schemas import MonoResultSchema
from ..base_endpoint import EndPoint, HTTPMethod

from database.models.payment.money_payment import MoneyPayment

from services.payment_service import PaymentServise
from services.character_service import CharacterService
from config import BOT_TOKEN

class MonoResultMoney(EndPoint):
    schema = MonoResultSchema
    data: MonoResultSchema
    method = HTTPMethod.POST
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    TEXT_TEMPLATE = """
<b>Ви оплатили замовлення, вам нараховано</b>: {amount_money} 💵
    """
    
    async def handle_request(self) -> Response:
        payment: MoneyPayment = await PaymentServise.get_payment(
            order_id=self.data.invoiceId,
            type_payment = MoneyPayment
        )
        
        if not payment:
            return
        
        if self.data.status != "success":
            return
        
        if payment.payment.status:
            return
        
        character = await CharacterService.get_character(payment.payment.user_id)
        
        await CharacterService.update_money_character(
            character_id = character.id,
            amount_money_adjustment = payment.count_money
        )
        await self.bot.send_message(
            chat_id = payment.payment.user_id,
            text    = self.TEXT_TEMPLATE.format(amount_money = payment.count_money)
        )
        await PaymentServise.change_payment_status(order_id=self.data.invoiceId)
        raise self.OK()
        
        


