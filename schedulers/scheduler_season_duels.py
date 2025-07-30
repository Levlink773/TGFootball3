import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from database.models.duel import Duel
from services.duel_service import DuelService

from database.models.character import Character
from services.character_service import CharacterService

from constants import DUEL_END_DAY_SEASON

from collections import defaultdict
from logging_config import logger
from loader import bot

from typing import List, Tuple

class SchedulerSesonDuels:
    scheduler = AsyncIOScheduler()
    winners_count = 10
    trigger = CronTrigger(day=DUEL_END_DAY_SEASON, hour=9, minute=0)
    
    rewards_top_user = {
        10: {'money': 10, 'energy': 0},
        9:  {'money': 15, 'energy': 0},
        8:  {'money': 20, 'energy': 0},
        7:  {'money': 25, 'energy': 0},
        6:  {'money': 30, 'energy': 0},
        5:  {'money': 35, 'energy': 100},
        4:  {'money': 40, 'energy': 130},
        3:  {'money': 45, 'energy': 180},
        2:  {'money': 55, 'energy': 250},
        1:  {'money': 60, 'energy': 300},
    }
    
    TEXT_REWARD_TEMPLATE = """<b>Вітаємо з блискучою перемогою!</b>     
🎉🎉 Ти показав свою силу та майстерність у ПВП-пеналті, і це твій заслужений тріумф! 🏆

За твоє місце в рейтингу ти отримав:

💰 {money} монет
{energy_text}

Продовжуй вражати нас своїми перемогами та досягненнями! Ти справжній чемпіон! 💪🔥
"""

    TEXT_ENERGY_TEMPLATE = "⚡ {energy} енергії"
    
    def _get_top_users(self, duels: list[Duel]) -> List[Tuple[Character, int]]:
        user_scores = defaultdict(int)
        
        for duel in duels:
            winners = duel.get_winner_duel
            if isinstance(winners, list): 
                for winner in winners:
                    user_scores[winner] += 1  
            else:
                user_scores[winners] += 3
        
        top_users = sorted(user_scores.items(), key=lambda x: x[1], reverse=True)
        return top_users[:self.winners_count]
    
    
    def _get_text(self, money: int, energy: int) -> str:
        
        energy_text = self.TEXT_ENERGY_TEMPLATE.format(energy=energy) if energy else ""
        return self.TEXT_REWARD_TEMPLATE.format(
            money=money,
            energy_text = energy_text
        )
        

    async def _send_message(cls, user_id: int, text: str) -> None:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=text
            )
        except Exception as E:
            logger.error("error send message to users")
    
    async def _distribute_rewards(self, winner_users: List[Tuple[Character, int]]):
        
        for index, (user, _) in enumerate(winner_users, start=1):
            reward = self.rewards_top_user.get(index)
            
            money  = reward['money']
            energy = reward['energy'] 
              
            await CharacterService.update_money_character(
                character_id=user.id,
                amount_money_adjustment=money
            )
            if energy:
                await CharacterService.edit_character_energy(
                    character_id  = user.id,
                    amount_energy = energy
                )
            
            text = self._get_text(money,energy)
                
            await self._send_message(
                user_id=user.characters_user_id,
                text=text
            )
            
    async def end_duel_season(self):
        logger.info("ОКАНЧИВАЮ СЕЗОН ДУЕЛЕЙ")
        duels = await DuelService.get_season_duels()
        winner_users = self._get_top_users(duels)
        await self._distribute_rewards(winner_users)
    
    async def wait_to_end_season_duel(self):
        self.scheduler.add_job(self.end_duel_season, self.trigger,misfire_grace_time = 10
)
        self.scheduler.start()
    