import asyncio

from aiogram import Bot
from aiohttp.web import Response
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from webhook_api.schemas import MonoResultSchema
from ..base_endpoint import EndPoint, HTTPMethod

from database.models.payment.box_payment import BoxPayment

from bot.routers.stores.box.open_box import OpenBoxService
from services.payment_service import PaymentServise
from services.character_service import CharacterService
from config import BOT_TOKEN
from constants import lootboxes

class MonoResultBox(EndPoint):
    schema = MonoResultSchema
    data: MonoResultSchema
    method = HTTPMethod.POST
    verify_signature = True
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    TEXT_TEMPLATE = """
<b>Ви оплатили замовлення, ви отримали</b>: {name_box}
Він буде автоматично відкритий через 30 сек
    """
    
    async def handle_request(self) -> Response:
        payment: BoxPayment = await PaymentServise.get_payment(
            order_id=self.data.invoiceId,
            type_payment = BoxPayment
        )
        
        if not payment:
            return self.OK()

        if self.data.status != "success":
            return self.OK()

        if payment.payment.status:
            return self.OK()

        character = await CharacterService.get_character(payment.payment.user_id)
        
        name_box = lootboxes[payment.type_box]['name_lootbox']
        await self.bot.send_message(
            chat_id = payment.payment.user_id,
            text    = self.TEXT_TEMPLATE.format(name_box = name_box)
        )
        open_box = OpenBoxService(
            type_box = payment.type_box,
            character = character,
            bot = self.bot
        )
        await PaymentServise.change_payment_status(order_id=self.data.invoiceId)

        # Open the box after a 30s delay without holding the webhook connection open.
        async def _delayed_open():
            await asyncio.sleep(30)
            await open_box.open_box()

        asyncio.create_task(_delayed_open())
        return self.OK()
