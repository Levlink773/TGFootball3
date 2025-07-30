from pydantic import BaseModel
import random

from .base_item import ITEM

    
class Box(BaseModel):
    items: list[ITEM]
    weighted_items: list[ITEM] = []
    min_items: int = 100
    
    def normalize_chances(self):
        total_chance = sum(item.chance for item in self.items)
        for item in self.items:
            item.chance = (item.chance / total_chance) * 100

    @property
    def all_chance_items(self) -> list[int]:
        return [item.chance for item in self.items]

    def _add_items(self):
        if len(self.weighted_items) < self.min_items:
            while len(self.weighted_items) < self.min_items:
                random_item = random.choices(self.items, weights=self.all_chance_items, k=1)[0]
                new_item = ITEM(
                    name=random_item.name,
                    chance=random_item.chance,
                    min=random_item.min,
                    max=random_item.max,
                    step_count=random_item.step_count,
                    description = random_item.description
                )
                new_item.count_item = new_item.get_count()
                self.weighted_items.append(new_item)
    
    @property
    def items_in_box(self) -> list[ITEM]:
        if not self.weighted_items:
            self.normalize_chances()
            self._add_items()
        return self.weighted_items
    
    @property
    def winner_items(self) -> list[ITEM]:
        return random.choices(self.items_in_box, k=10)      

  