from aiogram import Bot
from aiohttp.web import Response
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.routers.stores.vip_pass.types import VipPassTypes, vip_passes

from database.models.payment.vip_pass_payment import VipPassPayment

from services.payment_service import PaymentServise
from services.vip_pass_service import VipPassService
from services.character_service import CharacterService

from schedulers.scheduler_vip_pass import VipPassScheduler

from webhook_api.schemas import MonoResultSchema

from config import BOT_TOKEN

from ..base_endpoint import EndPoint, HTTPMethod


class MonoResultVipPass(EndPoint):
    schema = MonoResultSchema
    data: MonoResultSchema
    method = HTTPMethod.POST
    verify_signature = True
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    type_payment = VipPassPayment

    TEXT_TEMPLATE = """
<b>Вітаємо, ти став VIP на {duration} днів!</b>

Тепер ти отримуєш безліч переваг у грі, щоб ставати ще сильнішим та швидшим! Ось що чекає на тебе:

- <b>+150 енергії</b> щодня — тепер ти можеш проводити ще більше часу у грі та досягати великих результатів!
- <b>Х2 нагород</b> з навчального центру — подвоюй свої бонуси та прокачуйся швидше!
- <b>+5% успішності тренувань</b> — твої тренування стануть ще ефективнішими!
- <b>VIP статус</b> — твій нік тепер виділяється серед інших!

Ти зробив великий крок до того, щоб стати найкращим у грі! Бажаємо успіхів, твоя VIP-подорож тільки починається! ⚽💎
"""

    

    async def handle_request(self) -> Response:
        payment:VipPassPayment = await PaymentServise.get_payment(
            order_id=self.data.invoiceId,
            type_payment = self.type_payment
            )
        
        if not payment:
            return self.OK()

        if self.data.status != "success":
            return self.OK()

        if payment.payment.status:
            return self.OK()

        duration = vip_passes.get(payment.type_vip_pass).duration
        
        
        character = await CharacterService.get_character(payment.payment.user_id)
        await VipPassService.update_vip_pass_time(
            character = character,
            day_vip_pass = duration
        )
        await self.bot.send_message(
            chat_id = payment.payment.user_id,
            text    = self.TEXT_TEMPLATE.format(
                duration = duration
            )
        )
        await PaymentServise.change_payment_status(order_id=self.data.invoiceId)
        update_character = await CharacterService.get_character(payment.payment.user_id)
        vip_pass_reminder = VipPassScheduler(update_character)
        await vip_pass_reminder.start_taimer()
        return self.OK()
        


