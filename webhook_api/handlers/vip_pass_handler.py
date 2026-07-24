from aiogram import Bot
from aiohttp.web import Response
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from bot.routers.stores.vip_pass.types import VipPassTypes, vip_passes

from sqlalchemy import update, func, text

from database.models.payment.vip_pass_payment import VipPassPayment
from database.models.character import Character

from services.payment_service import PaymentServise
from services.vip_pass_service import VipPassService
from services.character_service import CharacterService

from schedulers.scheduler_vip_pass import VipPassScheduler

from webhook_api.schemas import MonoResultSchema

from config import BOT_TOKEN
from logging_config import logger

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

        duration = vip_passes.get(payment.type_vip_pass).duration

        character = await CharacterService.get_character(payment.payment.user_id)
        if not character:
            logger.error(
                "PAID BUT NOT CREDITED order_id=%s user_id=%s: no character",
                self.data.invoiceId, payment.payment.user_id,
            )
            return self.OK()

        # Claim + grant in ONE transaction. The new expiry is computed in SQL from the
        # stored value (extend if still active, else from now), so it cannot be
        # miscalculated from a stale read or lost to a crash between the two writes.
        # duration comes from the server-side vip_passes catalog, never the callback.
        applied = await PaymentServise.claim_and_apply(
            self.data.invoiceId,
            update(Character)
            .where(Character.id == character.id)
            .values(
                vip_pass_expiration_date=func.date_add(
                    func.greatest(
                        func.now(),
                        func.coalesce(Character.vip_pass_expiration_date, func.now()),
                    ),
                    text(f"INTERVAL {int(duration)} DAY"),
                )
            ),
        )
        if not applied:
            return self.OK()

        await self.bot.send_message(
            chat_id = payment.payment.user_id,
            text    = self.TEXT_TEMPLATE.format(
                duration = duration
            )
        )
        update_character = await CharacterService.get_character(payment.payment.user_id)
        vip_pass_reminder = VipPassScheduler(update_character)
        await vip_pass_reminder.start_taimer()
        return self.OK()
        


