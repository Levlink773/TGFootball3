import asyncio
from aiogram import Bot

from bot.boxes.base_open import OpenBox
from bot.boxes.base_box import Box
from bot.boxes.base_item import Energy, Exp, Money

from database.models.types import TypeBox
from database.models.character import Character

from services.character_service import CharacterService

from constants import lootboxes


def create_boxes(lootbox_data: TypeBox) -> list[Box]:
    info_lootbox = lootboxes.get(lootbox_data, None)
    
    energy = Box(
        items=[Energy(min=info_lootbox["min_energy"], max=info_lootbox["max_energy"])]
    )
    
    money = Box(
        items=[Money(min=info_lootbox["min_money"], max=info_lootbox["max_money"])]
    )
    
    exp = Box(
        items=[Exp(min=info_lootbox["min_exp"], max=info_lootbox["max_exp"])]
    )
    return energy, money, exp

class OpenBoxService:
    def __init__(
        self, 
        type_box: TypeBox,
        character: Character,
        bot: Bot
     ) -> None:
        self.type_box = type_box
        self.box_energy, self.box_money, self.box_exp = create_boxes(type_box)
        self.character = character
        self.bot = bot

    def get_frame_text(self):
        self.open_box_energy = OpenBox(items=self.box_energy.winner_items)
        self.open_box_money = OpenBox(items=self.box_money.winner_items)
        self.open_box_exp = OpenBox(items=self.box_exp.winner_items)

        frame_gen_energy = self.open_box_energy.get_next_frame()
        frame_gen_money = self.open_box_money.get_next_frame()
        frame_gen_exp = self.open_box_exp.get_next_frame()

        while True:
            try:
                frame_energy = next(frame_gen_energy).split("\n")[0]
                frame_money = next(frame_gen_money).split("\n")[0]
                frame_exp = next(frame_gen_exp)
                combined_frame = f"{frame_energy}\n{frame_money}\n{frame_exp}"
                yield combined_frame
            except StopIteration:
                break
    
    async def open_box(self):
        message = await self.bot.send_message(
            chat_id=self.character.characters_user_id,
            text="Відкриваю лутбокс..."
        )
        await asyncio.sleep(3)

        for num,frame in enumerate(self.get_frame_text()):
            if num % 2 == 0:
                await message.edit_text(
                    text=frame
                )
                await asyncio.sleep(0.35)
        await self._distribute_reward()
            
    async def _distribute_reward(self):
        await CharacterService.add_exp_character(
            character_id = self.character.id,
            amount_exp_add = self.open_box_exp.winner_item.count_item
        )
        await CharacterService.update_money_character(
            character_id = self.character.id,
            amount_money_adjustment = self.open_box_money.winner_item.count_item
        )
        await CharacterService.edit_character_energy(
            character_id = self.character.id,
            amount_energy = self.open_box_energy.winner_item.count_item
        )
        
        text = """
🔓 <b>Ви відкрили {name_box}</b>

Отримано

⚡ Енергія: {count_energy}
💰 Монети: {count_money}
🎓 Досвід: {count_exp}

Вітаємо! 🚀        
        """
        
        await self.bot.send_message(
            chat_id=self.character.characters_user_id,
            text=text.format(
                name_box=lootboxes[self.type_box]['name_lootbox'],
                count_energy=self.open_box_energy.winner_item.count_item,
                count_exp=self.open_box_exp.winner_item.count_item,
                count_money=self.open_box_money.winner_item.count_item
            )
        )
        
        