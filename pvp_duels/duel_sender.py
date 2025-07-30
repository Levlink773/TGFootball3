from enum import Enum

from pvp_duels.types import DuelUser, RoleDuel
from pvp_duels.contstans import (
    TIMES_SLEEP_ENTRY_DATA_DUEL,
    FORWARD_LOSS_GOAL,
    FORWARD_GOAL,
    GOALKEPEER_LOSS_GOAL,
    GOALKEPEER_GOAL
    
    )

from database.models.character import Character
from bot.keyboards.pvp_duels_keyboard import select_bit, select_position_angle
from loader import bot

from constants import DUEL_PHOTO

class TEXT_DUEL(Enum):
    message_select_bit = """
<b>Готові до ПВП-пеналті?</b> ⚽🔥

Два учасники готові зійтися в епічній футбольній битві, і тепер настав час зробити ставки!

<b>Загальна сила учасників</b>: 
{user_1_name} [{user_1_power:.2f}] [{user_1_position}] [{user_1_level}]
<u>VS</u>
{user_2_name} [{user_2_power:.2f}] [{user_2_position}] [{user_2_level}]

💥 <b>30</b> одиниць енергії – Консервативна ставка для тих, хто хоче боротися, але віддає перевагу збереженню сил на майбутнє.
⚖️ <b>50</b> одиниць енергії – Баланс між ризиком та впевненістю. Достатньо, щоб показати супернику свою рішучість!
🔥 <b>100</b> одиниць енергії – Агресивна ставка для тих, хто вірить у перемогу та готовий поставити все на кон!
🏆 <b>150</b> одиниць енергії – Максимальний ризик, максимальна нагорода. Це ставка для тих, хто прагне виграти будь-якою ціною!

Побідник забирає всю енергію суперника! <b>Обирайте свою ставку і готуйтеся до битви!</b> ⚔️
    """
    
    dont_select_bit = """
<b>Дуель скасовано!</b> ❌

На жаль, <b>{user_name}</b> не обрав кількість енергії для своєї ставки, тому футбольна дуель не може відбутися. 😔

Але не хвилюйся! Ти завжди можеш прийняти участь у нових битвах і показати всім свою майстерність на полі. 🏟️ Підготуйся до наступного виклику!    

Вашу енергію, якщо ви її поставили, було повернуто
    """
    
    text_forward = """
<b>Ваша позиція - <u>Нападаючий</u></b> ⚡
Ви - головний атакувальник, і ваша мета проста: забити гол за всяку ціну. 
Кожен ваш рух, кожен удар - це шанс на перемогу. 
Дійте рішуче, і нехай суперник побачить, що його захист безсилий перед вашим натиском!
    """
    
    text_goalkepeer = """
<b>Ваша позиція - <u>Воротар 🧤</u></b>
Ви - останній бастіон захисту. Ваше завдання - відбивати будь-які удари і не дати супернику забити. 
Кожна ваша дія може вирішити результат ПВП-пеналті. Будьте напоготові і доведіть, що ваші ворота непробивні!
    """
    

    text_select_position_angle_forward = """
Ви готові до удару! ⚽ В який бік ви відправите м'яч?

⬅️ <b>Вліво</b> – точний удар у лівий кут, змушуючи воротаря стрибнути в останній момент

➡️ <b>Вправо</b> – впевнений удар у правий кут, ставлячи захист під тиск

⬆️ <b>Вгору</b> – потужний удар у верхній кут, куди воротар навряд чи дістане

У вас є <b>{TIME_CHOISE_ANGLE} секунд</b>, щоб зробити вибір! ⏳

Обирайте, куди будете бити! 🥅
"""

    text_select_position_angle_goalkeeper = """
Суперник готується до удару, і вам потрібно вибрати сторону для стрибка! ⚠️

⬅️ <b>Вліво</b> – інстинктивний стрибок у лівий кут, щоб відбити небезпечний удар

➡️ <b>Вправо</b> – різкий стрибок у правий кут, де може полетіти м'яч

⬆️ <b>Вгору</b> – готовність до високого стрибка, щоб відбити м'яч, що летить у верхній кут

У вас є <b>{TIME_CHOISE_ANGLE} секунд</b>, щоб прийняти рішення! ⏳

Обирайте, в який бік будете відбивати м'яч! 🛡️
"""
        
    text_goal_scored = {
        RoleDuel.FORWARD: {
            "text" : (
                    "<b>Фантастичний удар! ⚽</b> М'яч пройшов оборону і влетів у ворота! 🎉\n"
                    "Ваш точний і потужний удар приніс вам <b>заслужене очко!</b> 🏆 "
                    "Продовжуйте в тому ж дусі — ви на шляху до перемоги! 🌟\n\n"
                    "<b>Рахунок ПВП-пеналті:</b> [{user_1_name}] <u>{points_user_1}</u> ➖ <u>{points_user_2}</u> [{user_2_name}]"),
            "photo" : FORWARD_GOAL}
                           
                           ,
        RoleDuel.GOALKEEPER:{
            "text": (
                    "М'яч у воротах! 😱 Суперник виявився швидшим, і його удар був\n"
                    "<b>надто точним.</b> 🎯 Цього разу не вдалося захистити ворота, "
                    "але це ще не кінець. <b>Підготуйтеся до наступного випробування!</b> 🔄\n\n"
                    "<b>Рахунок ПВП-пеналті:</b> [{user_1_name}] <u>{points_user_1}</u> ➖ <u>{points_user_2}</u> [{user_2_name}]"
                    ),
            "photo" : GOALKEPEER_LOSS_GOAL
                            }
    }

    text_no_goal = {
            RoleDuel.GOALKEEPER: {
                "text": (
                    "<b>Що за чудовий сейв! 🙌</b> Ви правильно обрали напрямок і відбили м'яч!\n"
                    "Суперник був близький до успіху, але ваша блискавична реакція врятувала гру. "
                    "<b>Чудовий захист!</b> 🛡️\n\n"
                    "<b>Рахунок ПВП-пеналті:</b> [{user_1_name}] <u>{points_user_1}</u> ➖ <u>{points_user_2}</u> [{user_2_name}]"
                ),
                "photo": GOALKEPEER_GOAL  # Исправлено на GOALKEEPER_GOAL
            },
            RoleDuel.FORWARD: {
                "text": (
                    "Мимо! 😔 Воротар вгадав ваш хід або м'яч пройшов повз ворота.\n"
                    "Це був сміливий удар, але цього разу <b>фортуна відвернулася від вас.</b> 🍀 "
                    "Не зупиняйтесь — <b>перемога ще можлива!</b> ✊\n\n"
                    "<b>Рахунок ПВП-пеналті:</b> [{user_1_name}] <u>{points_user_1}</u> ➖ <u>{points_user_2}</u> [{user_2_name}]"
                ),
                "photo": FORWARD_LOSS_GOAL
            }
        }
    victory_message = (
        "<b>Вітаємо з перемогою! 🎉</b>\n"
        "Ваша ставка в <b>{bid_user}</b> одиниць енергії принесла результат! "
        "Ви отримуєте <b>{double_bid_user}</b> одиниць енергії у вигляді винагороди за вашу "
        "<b>майстерність та рішучість.</b> Продовжуйте в тому ж дусі, і ваша енергія зростатиме!"
    )

    loss_message = (
        "<b>На жаль, ви програли. ❌</b>\n"
        "Ваша ставка в <b>{bid_user}</b> одиниць енергії не принесла результату, "
        "Не впадайте у відчай — <b>кожен програш — це шанс навчитися</b> та "
        "підготуватися до нових викликів!"
    )

    draw_message = (
        "<b>Нічия в ПВП-пеналті! ⚖️</b>\n"
        "Дуель закінчилася в нічию, і ваша ставка в <b>{bid_user}</b> одиниць енергії повертається до вас. "
        "Цей результат говорить про те, що <b>обидві сторони продемонстрували гідну гру.</b> "
        "Використайте цей час, щоб проаналізувати стратегію та підготуватися до наступних боїв!"
    )
        
    
class DuelSender:
    def __init__(self, duel_users: DuelUser) -> None:
        self.duel_users = duel_users
    
    async def send_messages_select_bit(self):
        for user in self.duel_users.all_users_duel:
            await bot.send_photo(
                chat_id=user.characters_user_id,
                photo=DUEL_PHOTO,
                caption = TEXT_DUEL.message_select_bit.value.format(
                    user_1_name     = self.duel_users.user_1.character_name ,
                    user_1_power    = self.duel_users.user_1.full_power,
                    user_1_position = self.duel_users.user_1.acronym_position,
                    user_1_level    = self.duel_users.user_1.level,
                    
                    user_2_name     = self.duel_users.user_2.character_name ,
                    user_2_power    = self.duel_users.user_2.full_power,
                    user_2_position = self.duel_users.user_2.acronym_position,
                    user_2_level    = self.duel_users.user_2.level,
                ),
                reply_markup=select_bit(duel_id=self.duel_users.duel_id)      
                )
            
    async def send_message_dont_select_bit(self, user_not_selected_bit: Character):
        for user in self.duel_users.all_users_duel:
            await bot.send_message(
                chat_id=user.characters_user_id,
                text=TEXT_DUEL.dont_select_bit.value.format(
                    user_name = user_not_selected_bit.character_name
                )
            )


    async def __send_message_to_roles(self, role, text, reply_markup=None, photo = None):
        user = self.duel_users.get_user_by_role(role=role)
        if not photo:
            await bot.send_message(
                chat_id=user.characters_user_id,
                text=text,
                reply_markup=reply_markup
            )
        else:
            await bot.send_photo(
                chat_id=user.characters_user_id,
                caption=text,
                photo=photo
            )
    async def send_message_to_roles(self):
        await self.__send_message_to_roles(RoleDuel.FORWARD, TEXT_DUEL.text_forward.value)
        await self.__send_message_to_roles(RoleDuel.GOALKEEPER, TEXT_DUEL.text_goalkepeer.value)

    async def send_message_select_angle(self):
        markup = select_position_angle(duel_id=self.duel_users.duel_id)
        await self.__send_message_to_roles(RoleDuel.FORWARD, 
            TEXT_DUEL.text_select_position_angle_forward.value.format(TIME_CHOISE_ANGLE=TIMES_SLEEP_ENTRY_DATA_DUEL), 
                                           markup)
        
        
        await self.__send_message_to_roles(RoleDuel.GOALKEEPER, 
            TEXT_DUEL.text_select_position_angle_goalkeeper.value.format(TIME_CHOISE_ANGLE=TIMES_SLEEP_ENTRY_DATA_DUEL)
                                           , markup)

    async def send_message_win_etap(self, winner_etap: RoleDuel):
        text_event_goal = TEXT_DUEL.text_goal_scored if winner_etap == RoleDuel.FORWARD else TEXT_DUEL.text_no_goal
        await self.__send_message_to_roles(
            RoleDuel.FORWARD, 
            text_event_goal.value[RoleDuel.FORWARD]['text'].format(
                    user_1_name   = self.duel_users.user_1.character_name,
                    points_user_1 = self.duel_users.points_user_1,
                    points_user_2 = self.duel_users.points_user_2,
                    user_2_name   = self.duel_users.user_2.character_name,
                                                                    ),
            photo=text_event_goal.value[RoleDuel.FORWARD]['photo']
                        
                                           )
        await self.__send_message_to_roles(
            RoleDuel.GOALKEEPER, 
            text_event_goal.value[RoleDuel.GOALKEEPER]['text'].format(
                user_1_name   = self.duel_users.user_1.character_name,
                points_user_1 = self.duel_users.points_user_1,
                points_user_2 = self.duel_users.points_user_2,
                user_2_name   = self.duel_users.user_2.character_name,
                                                            ),
            photo=text_event_goal.value[RoleDuel.GOALKEEPER]['photo']
            )
        
    async def send_message_end_duel(self, winner: Character| list[Character]):
        if isinstance(winner,list):
            await bot.send_message(
                chat_id=self.duel_users.user_1.characters_user_id,
                text=TEXT_DUEL.draw_message.value.format(bid_user = self.duel_users.bid_user_1)
            )  
            await bot.send_message(
                            chat_id=self.duel_users.user_2.characters_user_id,
                            text=TEXT_DUEL.draw_message.value.format(bid_user = self.duel_users.bid_user_2)
                        )   
        else:
            bid_winner_user = self.duel_users.bid_user_1 if winner.id == self.duel_users.user_1.id else self.duel_users.bid_user_2
            await bot.send_message(
                chat_id=winner.characters_user_id,
                text = TEXT_DUEL.victory_message.value.format(
                    bid_user = bid_winner_user,
                    double_bid_user = bid_winner_user*2
                )
            )
            oponent_user = self.duel_users.get_opponent(my_user=winner)
            bid_loser_user  = self.duel_users.bid_user_2 if winner.id == self.duel_users.user_2.id else self.duel_users.bid_user_1
            await bot.send_message(
                chat_id=oponent_user.characters_user_id,
                text=TEXT_DUEL.loss_message.value.format(
                    bid_user = bid_loser_user
                )
            )
            
