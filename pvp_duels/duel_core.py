import uuid
import asyncio

from database.models.character import Character
from services.character_service import CharacterService
from services.reminder_character_service import RemniderCharacterService

from pvp_duels.types import DuelUser
from pvp_duels.utils import select_random_roles
from pvp_duels.duel import Duel
from pvp_duels.duel_sender import DuelSender
from pvp_duels.duel_manager import DuelManager

from logging_config import logger


class CoreDuel:
    count_users_duel = 2
    queue_users_duel = asyncio.Queue()
    
    @classmethod
    async def is_in_queue(cls, character: Character):
        temp_list = []
        found = False

        while not cls.queue_users_duel.empty():
            character_pool: Character = await cls.queue_users_duel.get()
            if character_pool.id == character.id:
                found = True
            temp_list.append(character_pool)
        
        for character_in_queue in temp_list:
            await cls.queue_users_duel.put(character_in_queue)

        return found

    @classmethod
    async def add_user_to_pool(cls, character: Character) -> bool:
        await cls.queue_users_duel.put(character)
        
    @classmethod
    async def remove_user_from_pool(cls, character: Character):
        users_batch: list[Character] = []
        while not cls.queue_users_duel.empty():
            user = await cls.queue_users_duel.get()
            users_batch.append(user)
            
        users_batch = [user for user in users_batch if user.id != character.id]    
        for user in users_batch:
            await cls.queue_users_duel.put(user)

        
    async def _waiting_users(self):
        while True:
            try:
                while self.queue_users_duel.qsize() < self.count_users_duel:
                    await asyncio.sleep(2)
                
                batch:list[Character] = []
                for _ in range(self.count_users_duel):
                    user_duel = await self.queue_users_duel.get()
                    batch.append(user_duel)
                await self.initialization_duel(*batch)
                batch.clear()
                await asyncio.sleep(1)
            except Exception as E:
                logger.error(f"error initialization duel err: {E}")
            
    async def initialization_duel(self, user_1: Character, user_2: Character):
        random_roles = select_random_roles() 
        duel_users = DuelUser(
            duel_id     = str(uuid.uuid4()),
            user_1      = user_1,
            role_user_1 = random_roles[0], 
            
            user_2      = user_2,
            role_user_2 = random_roles[1]
            )
        
        duel_sender = DuelSender(
            duel_users=duel_users
        )
        await duel_sender.send_messages_select_bit()
        DuelManager.add_pool_duel(duel_users.duel_id, duel_users)
        
        asyncio.create_task(self._wait_users_select_bit(duel_users, duel_sender))
        
    async def __back_energy_from_users(self, duel_users: DuelUser):
        DuelManager.delete_pool_duel(duel_id=duel_users.duel_id)
        if duel_users.bid_user_1:
            character = await CharacterService.get_character_by_id(character_id=duel_users.user_1.id)
            await CharacterService.edit_character_energy(
                character_id=character.id,
                amount_energy=duel_users.bid_user_1
            )
        if duel_users.bid_user_2:
            character = await CharacterService.get_character_by_id(character_id=duel_users.user_2.id)
            await CharacterService.edit_character_energy(
                character_id = character.id,
                amount_energy = duel_users.bid_user_2
            )
        for user in duel_users.all_users_duel:
            await RemniderCharacterService.edit_status_duel_character(
                character_id=user.id,
                status=False
            )
        
    async def _wait_users_select_bit(self, duel_users: DuelUser, duel_sender: DuelSender):
        await asyncio.sleep(30)
        if duel_users.bid_user_1 is None or duel_users.bid_user_2 is None:
            
            await self.__back_energy_from_users(duel_users)
            return await duel_sender.send_message_dont_select_bit(
                user_not_selected_bit = duel_users.user_1 if duel_users.bid_user_1 is None else duel_users.user_2
            ) 
        await self.starting_duel(duel_users, duel_sender)

    async def starting_duel(self, duel_users: DuelUser, duel_sender: DuelSender):
        duel = Duel(
            user_duel=duel_users,
            duel_sender = duel_sender
        )
        await duel.start_duel()