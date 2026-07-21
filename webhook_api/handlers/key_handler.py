from aiogram import Bot
from aiohttp.web import Response
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from webhook_api.schemas import MonoResultSchema
from ..base_endpoint import EndPoint, HTTPMethod

from bot.training.routers.utils import get_near_end_time_training
from bot.training.keyboard.keyboard_re_invite import join_to_training

from database.models.payment.key_payment import KeyPayment

from services.payment_service import PaymentServise
from services.character_service import CharacterService
from config import BOT_TOKEN


BASE_TEXT_TEMPLATE = """
🔑 <b>Ключ придбано!</b> ⚽🔥  

Вітаємо! Ти успішно купив ключ для входу на тренування. 🚀  
Тепер ти можеш приєднатися до найближчої сесії та покращити свої навички! 💪⚡  

⏳ <i>Слідкуй за розкладом та будь готовий увійти в гру!</i> 🏆
"""

TEXT_TEMPLATE_TRAINING_ACTIVE = """
🩳 Наразі активна сесія тренувань. Ви можете приєднатися до неї, використовуючи ключ.
"""


class MonoResultBuyTrainingKey(EndPoint):
    schema = MonoResultSchema
    data: MonoResultSchema
    method = HTTPMethod.POST
    verify_signature = True
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))



    async def handle_request(self) -> Response:
        payment: KeyPayment = await PaymentServise.get_payment(
            order_id=self.data.invoiceId,
            type_payment = KeyPayment
        )
        
        if not payment:
            return self.OK()

        if self.data.status != "success":
            return self.OK()

        if payment.payment.status:
            return self.OK()

        character = await CharacterService.get_character(payment.payment.user_id)
        await CharacterService.add_trainin_key(
            character_id = character.id,
        )
        text = BASE_TEXT_TEMPLATE
        keyboard = None
        
        near_training_end_time, is_active =  get_near_end_time_training()        
        if is_active:
            
            text += TEXT_TEMPLATE_TRAINING_ACTIVE
            keyboard = join_to_training(near_training_end_time)
            
        await self.bot.send_message(
            chat_id = payment.payment.user_id,
            text    = text,
            reply_markup = keyboard
        )
        await PaymentServise.change_payment_status(order_id=self.data.invoiceId)
        return self.OK()


