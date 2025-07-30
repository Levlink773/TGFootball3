from aiogram import Bot
from aiohttp.web import Response
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from webhook_api.schemas import MonoResultSchema
from ..base_endpoint import EndPoint, HTTPMethod

from database.models.payment.energy_payment import EnergyPayment

from services.payment_service import PaymentServise
from services.character_service import CharacterService
from config import BOT_TOKEN

class MonoResultEnergy(EndPoint):
    schema = MonoResultSchema
    data: MonoResultSchema
    method = HTTPMethod.POST
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    TEXT_TEMPLATE = """
<b>Ви оплатили замовлення, вам нараховано</b>: {amount_energy} 🔋
    """
    
    async def handle_request(self) -> Response:
        payment: EnergyPayment = await PaymentServise.get_payment(
            order_id=self.data.invoiceId,
            type_payment = EnergyPayment
        )
        
        if not payment:
            return
        
        if self.data.status != "success":
            return
        
        if payment.payment.status:
            return
        
        character = await CharacterService.get_character(payment.payment.user_id)
        
        await CharacterService.edit_character_energy(
            character_id  = character.id,
            amount_energy = payment.amount_energy
        )
        await self.bot.send_message(
            chat_id = payment.payment.user_id,
            text    = self.TEXT_TEMPLATE.format(amount_energy = payment.amount_energy)
        )
        await PaymentServise.change_payment_status(order_id=self.data.invoiceId)
        return self.OK()
        
        


