import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.models.character import Character

from services.character_service import CharacterService
from services.club_service import ClubService

from constants import TIME_RESET_ENERGY_CHARACTER, TIME_RESET_ENERGY_CLUB
from logging_config import logger
from utils.notify import notify_many


class EnergyResetScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    # Текст описывает то, что реально делает апдейт: энергия ВЫСТАВЛЯЕТСЯ в кап,
    # и тем, у кого её было больше, не меняется вообще.
    TEXT_REGULAR = (
        "🔋 Енергію відновлено до <b>150</b> ⚡️\n\n"
        "Якщо в тебе було більше — нічого не змінилось.\n"
        "Заходь тренуватись і реєструйся на матч! ⚽️"
    )
    TEXT_VIP = (
        "👑 <b>VIP</b> — енергію відновлено до <b>300</b> ⚡️\n\n"
        "Якщо в тебе було більше — нічого не змінилось.\n"
        "Уперед за перемогами! 🏆"
    )

    async def __send_message_bot(
        self,
        characters: list[Character],
        is_vip: bool
    ):
        text = self.TEXT_VIP if is_vip else self.TEXT_REGULAR
        sent = await notify_many(
            characters,
            text,
            screen="training",
            button_text="⚡️ У гру",
        )
        logger.info(f"Energy reset DM: {sent}/{len(characters)} (vip={is_vip})")

    async def reset_energy_character(self):
        # Порядок важен: когорты считаются ДО апдейта, иначе фильтр по энергии пуст.
        regular, vip = await CharacterService.get_characters_energy_restored()
        await CharacterService.update_energy_for_non_bots()
        asyncio.create_task(self.__send_message_bot(regular, False))
        asyncio.create_task(self.__send_message_bot(vip, True))
        logger.info("Обновил енергию для пользователей")
        
        
    async def start_reset_energy(self):
        self.scheduler.add_job(self.reset_energy_character, 
                               TIME_RESET_ENERGY_CHARACTER,
                               misfire_grace_time = 10
)
        self.scheduler.start()

        
        
class EnergyApliedClubResetScheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        
    async def reset_energy_aplied(self):
        await ClubService.reset_energy_aplied_not_bot_clubs()
        logger.info("Убрал усиление с команд")

    async def start_reset_energy(self):
        self.scheduler.add_job(self.reset_energy_aplied, 
                               TIME_RESET_ENERGY_CLUB,
                                misfire_grace_time = 10
)
        self.scheduler.start()
