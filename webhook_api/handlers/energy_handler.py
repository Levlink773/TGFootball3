from aiogram import Bot
from aiohttp.web import Response
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from webhook_api.schemas import MonoResultSchema
from ..base_endpoint import EndPoint, HTTPMethod

from sqlalchemy import update, func

from database.models.payment.energy_payment import EnergyPayment
from database.models.character import Character

from services.payment_service import PaymentServise
from services.character_service import CharacterService
from config import BOT_TOKEN, CONST_ENERGY, CONST_VIP_ENERGY
from logging_config import logger

class MonoResultEnergy(EndPoint):
    schema = MonoResultSchema
    data: MonoResultSchema
    method = HTTPMethod.POST
    verify_signature = True
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
            return self.OK()

        if self.data.status != "success":
            return self.OK()

        character = await CharacterService.get_character(payment.payment.user_id)
        if not character:
            logger.error(
                "PAID BUT NOT CREDITED order_id=%s user_id=%s: no character",
                self.data.invoiceId, payment.payment.user_id,
            )
            return self.OK()

        # Claim + credit in ONE transaction. LEAST() applies the tier cap in SQL so
        # the clamp cannot be lost to a concurrent write.
        cap = CONST_VIP_ENERGY if character.vip_pass_is_active else CONST_ENERGY
        credited = await PaymentServise.claim_and_apply(
            self.data.invoiceId,
            update(Character)
            .where(Character.id == character.id)
            .values(
                current_energy=func.least(
                    cap, Character.current_energy + payment.amount_energy
                )
            ),
        )
        if not credited:
            return self.OK()

        await self.bot.send_message(
            chat_id = payment.payment.user_id,
            text    = self.TEXT_TEMPLATE.format(amount_energy = payment.amount_energy)
        )
        return self.OK()
        
        


