import asyncio
import uuid

from utils.randomaizer import check_chance

from pvp_duels.types import DuelUser, RoleDuel
from pvp_duels.utils import select_random_angle
from pvp_duels.duel_sender import DuelSender
from pvp_duels.duel_manager import DuelManager
from pvp_duels.contstans import (
    PERIOD_ETUP,
    PERIOD_ETAP_FIGHT_DUEL,
    TIMES_SLEEP_ENTRY_DATA_DUEL,
    PROCENT_KICK_GOAL,
    PROCENT_GOAL
        )
from database.models.character import Character
from services.reminder_character_service import RemniderCharacterService
from services.character_service import CharacterService
from services.duel_service import DuelService


class Duel:    
    def __init__(self, user_duel: DuelUser, duel_sender: DuelSender) -> None:
        self.user_duel = user_duel
        self.duel_sender = duel_sender

    async def _waiting_data_entry(self):
        await asyncio.sleep(TIMES_SLEEP_ENTRY_DATA_DUEL)
        if self.user_duel.position_angle_user_1 is None:
            self.user_duel.position_angle_user_1 = select_random_angle()
            
        if self.user_duel.position_angle_user_2 is None:
            self.user_duel.position_angle_user_2 = select_random_angle()
        
    async def start_duel(self) -> Character:  
        for _ in range(PERIOD_ETUP):
            await self.duel_sender.send_message_to_roles()      
            await self._start_etup()
            self.user_duel.change_roles_character()
            await asyncio.sleep(5)
        
        winner_duel = self.get_winner_duel()
        await self._end_duel(winner_duel)
        await DuelService.create_duel(
            duel_id      = self.user_duel.duel_id,
            user_1_id    = self.user_duel.user_1.id,
            user_2_id    = self.user_duel.user_2.id,
            point_user_1 = self.user_duel.points_user_1,
            point_user_2 = self.user_duel.points_user_2,
            bit_user_1   = self.user_duel.bid_user_1,
            bit_user_2   = self.user_duel.bid_user_2,
        )
        await self.duel_sender.send_message_end_duel(winner=winner_duel)
        
    
    async def _end_duel(self, winner_duel: Character | list[Character]):
        if isinstance(winner_duel, list):
            user_1 = await CharacterService.get_character_by_id(character_id=self.user_duel.user_1.id)
            await CharacterService.edit_character_energy(
                character_id  = user_1.id, 
                amount_energy = self.user_duel.bid_user_1
            )
            
            user_2 = await CharacterService.get_character_by_id(character_id=self.user_duel.user_2.id)
            await CharacterService.edit_character_energy(
                character_id  = user_2.id, 
                amount_energy = self.user_duel.bid_user_2
            )
        else:
            user_winner = await CharacterService.get_character_by_id(character_id=winner_duel.id)
            bid_winner_user = self.user_duel.bid_user_1 if winner_duel.id == self.user_duel.user_1.id else self.user_duel.bid_user_2
            await CharacterService.edit_character_energy(
                character_id  = user_winner.id, 
                amount_energy = bid_winner_user*2
            )
        
        for user in self.user_duel.all_users_duel:
            
            await RemniderCharacterService.edit_status_duel_character(
                character_id=user.id,
                status=False
            )
        DuelManager.delete_pool_duel(duel_id=self.user_duel.duel_id)
        
        
        
    async def _start_etup(self):
        for _ in range(PERIOD_ETAP_FIGHT_DUEL):
            await asyncio.sleep(5)
            await self.duel_sender.send_message_select_angle()
            await self._waiting_data_entry()
            
            winner_etap = self._choise_etap_win()
            if winner_etap == RoleDuel.FORWARD:
                self.user_duel.add_points_to_role(winner_etap, 1)
            await self.duel_sender.send_message_win_etap(winner_etap)
            
            self.user_duel.anulate_angle_users()
            await asyncio.sleep(3)
          
          
    def get_winner_duel(self) -> list[Character] | Character:
        if self.user_duel.points_user_1 == self.user_duel.points_user_2:
            return [self.user_duel.user_1, self.user_duel.user_2]
        elif self.user_duel.points_user_1 > self.user_duel.points_user_2:
            return self.user_duel.user_1
        else:
            return self.user_duel.user_2
        
    def _choise_etap_win(self) -> RoleDuel:
        user_goalkepper = self.user_duel.get_user_by_role(role=RoleDuel.GOALKEEPER)
        user_forward = self.user_duel.get_user_by_role(role=RoleDuel.FORWARD)
        
        power_forward = user_forward.full_power
        power_goalkepper = user_goalkepper.full_power
        
        if self.user_duel.position_angle_user_1 == self.user_duel.position_angle_user_2:     
            power_goalkepper += power_goalkepper * (PROCENT_KICK_GOAL / 100)
        else:
            power_forward += power_forward * (PROCENT_GOAL / 100)
        
        total_power = power_forward+power_goalkepper
        
        chance_win_forward = (power_forward/total_power) * 100 
        forward_is_win = check_chance(chance_win_forward)
        
        winner_etap =  RoleDuel.FORWARD if forward_is_win else RoleDuel.GOALKEEPER
        return winner_etap
        
