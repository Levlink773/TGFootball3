from aiogram import Router, F
from aiogram.types import CallbackQuery

from api.monobank.create_payment import CreatePayment

from bot.callbacks.change_position_callbacks import SelectPosition
from bot.keyboards.change_position_keyboard import (
    select_position,
    buy_change_position
)

from database.models.character import Character

from services.payment_service import PaymentServise

from constants import (
    CHANGE_POSITION_PHOTO, 
    PRICE_CHANGE_POSITION, 
    PositionCharacter
)
from config import (
    CALLBACK_URL_WEBHOOK_CHANGE_POSITION, 
    POSITION_COEFFICIENTS
) 


change_position_router = Router()

@change_position_router.callback_query(
    F.data == "change_position"
)
async def change_position_handler(
    query: CallbackQuery,
    character: Character
):
    text = f"""
Стань легендою футбольного поля! 🏆

Хочеш вивести свого персонажа на новий рівень? 🔥 Змінюй позицію і стань гравцем, який творить історію! Від надійного захисника до молниєносного нападника – тепер ти вирішуєш, як буде розвиватися твоя кар'єра в грі.

💼 Що ти отримаєш:
✅ Нові ігрові можливості.
✅ Перевагу в матчах та турнірах.

💰 Ціна зміни позиції – всього <s><b>250</b></s> (<u><b>{PRICE_CHANGE_POSITION}</b></u>) грн!
Один раз змінивши позицію, ти зможеш поглянути на гру з іншого боку і отримати максимум задоволення від кожного матчу.

📲 Не пропусти шанс!
"""

    await query.message.answer_photo(
        photo=CHANGE_POSITION_PHOTO,
        caption = text,
        reply_markup = select_position(character.position_enum)
    )
    
    
@change_position_router.callback_query(
    SelectPosition.filter()
)
async def select_new_position(
    query: CallbackQuery,
    character: Character,
    callback_data: SelectPosition
):
    
    text = """
🚨 <b>Увага!</b> 🚨
Після зміни позиції, характеристики твого персонажа можуть змінитися. Будь готовий до того, що твою бойову силу тепер визначатимуть нові коефіцієнти для кожної з позицій!

🔻 Зміни в характеристиках:
<b>🎯 Техніка:</b> Твоя здатність контролювати м'яч, здійснювати точні передачі
Значення до зміни: [{old_technique:.2f}] -> Значення після зміни: [{new_technique:.2f}]
 
<b>🥋 Удари:</b> Твоя сила ударів по воротах зміняться
Значення до зміни: [{old_effective_kicks:.2f}] -> Значення після зміни: [{new_effective_kicks:.2f}]

<b>🛡️ Відбір м’яча:</b> Позиція змінює ефективність вибору м'яча.
Значення до зміни: [{old_effective_ball_selection:.2f}] -> Значення після зміни: [{new_effective_ball_selection:.2f}]

<b>🏃 Витривалість:</b> Твоя здатність витримувати фізичне навантаження зміниться.
Значення до зміни: [{old_effective_endurance:.2f}] -> Значення після зміни: [{new_effective_endurance:.2f}]

<b>⚡ Швидкість:</b> Твоя здатність рухатися по полю тепер відображатиме нові можливості.
Значення до зміни: [{old_effective_speed:.2f}] -> Значення після зміни: [{new_effective_speed:.2f}]
""".format(
    old_technique        = get_params(character.technique, character.position_enum, "technique"),
    old_effective_kicks = get_params(character.kicks, character.position_enum, "kicks"),
    old_effective_ball_selection = get_params(character.ball_selection, character.position_enum, "ball_selection"),
    old_effective_endurance = get_params(character.endurance, character.position_enum, "endurance"),
    old_effective_speed = get_params(character.speed, character.position_enum, "speed"),
    
    new_technique       = get_params(character.technique, callback_data.position, "technique"),
    new_effective_kicks = get_params(character.kicks, callback_data.position, "kicks"),
    new_effective_ball_selection = get_params(character.ball_selection, callback_data.position, "ball_selection"),
    new_effective_endurance = get_params(character.endurance, callback_data.position, "endurance"),
    new_effective_speed = get_params(character.speed, callback_data.position, "speed")
)
    payment = CreatePayment(
        price=PRICE_CHANGE_POSITION,
        name_product="Зміна позіції",
        webhook_url=CALLBACK_URL_WEBHOOK_CHANGE_POSITION
    )
    url_payment_response = await payment.send_request()
    if not url_payment_response:
        return await query.answer("Сталася помилка під час створення платежу")
    
    order_id = url_payment_response['invoiceId']
    url_payment = url_payment_response['pageUrl']
    
    await query.message.edit_caption(
        caption=text,
        reply_markup=buy_change_position(
            url_payment=url_payment,
            new_position_name = callback_data.position.value
        )

    )
    payment = await PaymentServise.create_payment(
        price    = PRICE_CHANGE_POSITION,
        user_id  = character.characters_user_id,
        order_id = order_id,
    )
    
    await PaymentServise.create_change_position_payment(
        order_id = payment.order_id,
        position = callback_data.position
    )

def get_params(
    old_params: int,
    position: PositionCharacter,
    name_params: str
) -> int:
    
    return old_params * POSITION_COEFFICIENTS[position].get(name_params,1)