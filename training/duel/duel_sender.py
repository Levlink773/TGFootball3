from enum import Enum
from typing import Optional

from aiogram import Bot
from aiogram.types import FSInputFile, InlineKeyboardButton

from bot.training.keyboard.duel_training import (
    select_position_angle,
    end_duel_training
)

from training.types import Stage
from training.core.training import Training
from training.constans import (
    FORWARD_LOSS_GOAL,
    FORWARD_GOAL,
    GOALKEPEER_LOSS_GOAL,
    GOALKEPEER_GOAL,
    TIMES_SLEEP_ENTRY_DATA_DUEL,
    SCORE_WINNER_DUEL_STAGE,
    PHOTO_FORWARD,
    PHOTO_GOALKEEPER
)

from loader import bot
from logging_config import logger

from .types import DuelData, RoleDuel, DuelUser


class TEXT_DUEL:

    text_prewiew = {
        RoleDuel.FORWARD : """
<b>Ваша позиція – <u>Нападник</u></b> ⚡  
Тренер ставить м’яч на 11-метрову позначку. Ви робите кілька глибоких вдихів і готуєтеся до удару.  
Перед вами – воротар, який намагається вгадати ваш намір.  
Тренер уважно стежить за вашою технікою.  
""",
    
        RoleDuel.GOALKEEPER : """
<b>Ваша позиція – <u>Воротар</u></b> 🧤  
Ви займаєте місце у воротах, уважно стежите за нападником і чекаєте його удару.  
Тренер оцінює вашу реакцію, стійку та вміння читати суперника.   
"""
    }
    

    text_select_position_angle = {
        RoleDuel.FORWARD : """
Ви зосереджені, м’яч перед вами. 🏆 Тепер головне – вибрати напрям удару!  

⬅️ <b>Вліво</b> – обманний удар у лівий кут, змушуючи воротаря реагувати в останній момент.  

➡️ <b>Вправо</b> – різкий удар у правий кут, змушуючи суперника помилитися.  

⬆️ <b>Вгору</b> – потужний удар у верхній кут, майже недосяжний для воротаря.  

У вас є <b>{TIME_CHOISE_ANGLE} секунд</b>, щоб прийняти рішення! ⏳  
Обирайте напрямок і бийте! ⚽🥅  
""",

        RoleDuel.GOALKEEPER : """
Нападник наближається до м’яча, ви уважно стежите за його рухами. 🧤  
Зараз усе залежить від вашого вибору – куди ви стрибнете?  

⬅️ <b>Вліво</b> – блискавична реакція, стрибок у лівий кут для сейву.  

➡️ <b>Вправо</b> – різкий ривок у правий кут, щоб зупинити удар.  

⬆️ <b>Вгору</b> – стрибок під перекладину, аби врятувати команду від гола.  

У вас є <b>{TIME_CHOISE_ANGLE} секунд</b>, щоб ухвалити рішення! ⏳  
Готуйтеся – удар буде будь-якої миті! ⚽🥅  
"""
}
        
    text_goal_scored = {
        RoleDuel.FORWARD: {
            "text" : (
                "<b>Фантастичний удар! ⚽</b> М’яч пролітає повз воротаря і опиняється у сітці! 🎉\n"
                "Ваша техніка і точність приносять <b>+{points_scored} очок</b> до загального результату. 🏆\n"
                "Ваш поточний рахунок за тренування: <b>{total_points}</b> очок. 📈\n\n"
            ),
            "photo" : FORWARD_GOAL
        },
        RoleDuel.GOALKEEPER:{
            "text": (
                "<b>Неймовірний сейв! 🧤</b> Ви вгадали напрям удару і врятували ворота! 🚀\n"
                "Ваша реакція та майстерність приносять <b>+{points_scored} очок</b> до загального результату. 🏆\n"
                "Ваш поточний рахунок за тренування: <b>{total_points}</b> очок. 📈\n\n"
                    ),
            "photo" : GOALKEPEER_GOAL
                            }
    }

    text_no_goal = {
            RoleDuel.GOALKEEPER: {
                "text": (
                    "<b>Не вдалося відбити удар! 😟</b> М’яч проскакує повз вас і опиняється у сітці... ⚽\n"
                    "Ви стрибнули, але цього разу суперник переграв вас. Не засмучуйтеся, кожна спроба – це досвід! 💪\n"
                    "Проаналізуйте рух нападника, і наступного разу ви точно зупините удар! 🔥\n\n"
                    "<b>Ваш загальний рахунок за тренування:</b> <b>{total_points}</b> очок. 📈\n\n"
                ),
                "photo": GOALKEPEER_LOSS_GOAL
            },
            RoleDuel.FORWARD: {
                "text": (
                    "<b>Удар не вдався! 😔</b> Воротар вгадав напрямок або м’яч пройшов повз ворота.\n"
                    "Цього разу ви не заробили очки, але не втрачайте мотивації! 💪\n"
                    "Тренер підкаже, як покращити удар, щоб наступного разу м’яч точно опинився у сітці! ⚽🔥\n\n"
                    "<b>Ваш загальний рахунок за тренування:</b> <b>{total_points}</b> очок. 📈\n\n"
                ),
                "photo": FORWARD_LOSS_GOAL
            }
        }
    text_training_end = (
        "<b>Тренування завершено! 🏁</b>\n\n"
        "Ви добре попрацювали на полі, продемонструвавши свої навички та реакцію! ⚽🔥\n"
        "За цю пвп сесію ви заробили <b>{total_points_duel_training}</b> очок. 📈\n\n"
        "Пам’ятайте, що кожне тренування наближає вас до майстерності. Продовжуйте вдосконалювати свої удари та сейви, "
        "і на наступному тренуванні ви будете ще кращими! 💪⚡"
    )
        
    
class DuelSender:
    _bot: Bot = bot
    
    PHOTO_ROLES = {
        RoleDuel.FORWARD : PHOTO_FORWARD,
        RoleDuel.GOALKEEPER : PHOTO_GOALKEEPER
    }
    
    def __init__(
        self, 
        duel_data: DuelData,
        training: Training
    ) -> None:
        self.duel_data = duel_data
        self.training = training    
        
    async def send_message_role(self):
        for role in RoleDuel:
            user = self.duel_data.get_user_by_role(role)
            
            if user.is_bot:
                continue
            
            text: str = TEXT_DUEL.text_prewiew[role]
            await self._send_message(
                user = user,
                text = text,
                photo = self.PHOTO_ROLES[role]
            )

    async def send_message_select_angle(self):
        markup = select_position_angle(
            duel_id=self.duel_data.duel_id,
            end_time_health = self.training.end_time_from_keyboard
        )
        for role in RoleDuel:
            user = self.duel_data.get_user_by_role(role)
            if user.is_bot:
                continue
            
            text: str = TEXT_DUEL.text_select_position_angle[role]
            await self._send_message(
                user = user,
                text = text.format(TIME_CHOISE_ANGLE=TIMES_SLEEP_ENTRY_DATA_DUEL),
                keyboard = markup
            )

    async def send_itogs_etap(self, winner: DuelUser):
        for user in self.duel_data.all_users:
            try:
                if user.is_bot:
                    continue
                
                if user.user_id == winner.user_id:
                    text: str = TEXT_DUEL.text_goal_scored[user.pvp_role]['text'].format(
                        points_scored = SCORE_WINNER_DUEL_STAGE,
                        total_points = self.training.score
                    )
                else:
                    text: str = TEXT_DUEL.text_no_goal[user.pvp_role]['text'].format(
                        total_points = self.training.score
                    )
                    
                await self._send_message(
                    user =  user,
                    text = text
                )
            except Exception as E:
                logger.error(E)
                
    async def send_end_training_duel(self):
        try:
            keyboard = end_duel_training(
                end_time_health = self.training.end_time_from_keyboard,
                count_score = self.training.score,
                next_stage = Stage.END_TRAINIG
            )
        except Exception as E:
            logger.error(E)
        for user in self.duel_data.all_users:
            if user.is_bot:
                continue

            text: str = TEXT_DUEL.text_training_end.format(
                total_points_duel_training = user.points
            )
            await self._send_message(
                user = user,
                text = text,
                keyboard = keyboard
            )

    async def _send_message(self,
        user: DuelUser,
        text: str, 
        photo: Optional[FSInputFile] = None, 
        keyboard: Optional[InlineKeyboardButton]  = None    
    ):
        try:
            if photo:
                return await self._bot.send_photo(
                    chat_id=user.user_id,
                    photo=photo,
                    caption=text,
                    reply_markup=keyboard
                )
            await self._bot.send_message(
                chat_id=user.user_id,
                text=text,
                reply_markup=keyboard
            )
        except Exception as E:
            logger.error(f"Failed to send message to {user.user_id}\nError: {E}")
        
            
