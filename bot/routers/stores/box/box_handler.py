from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from api.monobank.create_payment import CreatePayment

from bot.callbacks.magazine_callbacks import SelectBox
from bot.keyboards.magazine_keyboard import buy_box

from database.models.character import Character

from services.payment_service import PaymentServise

from constants import lootboxes
from config import CALLBACK_URL_WEBHOOK_BOX


open_box_roter = Router()

TEXT_TEMPLATE = """
🎁 <b>Лутбокс</b>: {name_lootbox}

⚡ <b>Енергія</b>: {min_energy} - {max_energy} 💥  
💰 <b>Монети</b>: {min_money} - {max_money} 💎  
🎓 <b>Досвід</b>: {min_exp} - {max_exp} 📈  

💸 <b>Ціна</b>: СКИДКА 50% <del>{old_price}</del> - <b>{price}</b> UAH
"""


@open_box_roter.callback_query(SelectBox.filter())
async def select_box_handler(
    query: CallbackQuery,
    callback_data: SelectBox,
    character: Character
):
    type_box = callback_data.type_box
    price_box = lootboxes[type_box]['price']
    
    text_lootbox = TEXT_TEMPLATE.format(
        **lootboxes.get(callback_data.type_box), 
        old_price = int(price_box*2)
    )

    payment = CreatePayment(
        price=price_box,
        name_product=lootboxes[type_box]['name_lootbox'],
        webhook_url=CALLBACK_URL_WEBHOOK_BOX
    )
    url_payment_response = await payment.send_request()
    if not url_payment_response:
        return await query.answer("Сталася помилка під час створення платежу")
    
    order_id = url_payment_response['invoiceId']
    url_payment = url_payment_response['pageUrl']
    
    await query.message.edit_caption(
        caption=text_lootbox,
        reply_markup=buy_box(url_payment)

    )
    payment = await PaymentServise.create_payment(
        price    = price_box,
        user_id  = character.characters_user_id,
        order_id = order_id,
    )
    
    await PaymentServise.create_box_payment(
        order_id = payment.order_id,
        type_box = type_box
    )