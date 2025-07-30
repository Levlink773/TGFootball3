from sqlalchemy import Column, BigInteger, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship

from database.model_base import Base

import json

class Item(Base):
    __tablename__ = 'items'

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(255), index=True)
    category = Column(Enum('T_SHIRT', 'SHORTS', 'GAITERS', 'BOOTS', name='itemcategory'))
    level_required = Column(Integer, default=0)
    price = Column(Integer, default=0)
    stats = Column(String(255))
        
    owner_character_id = Column(BigInteger)

    @property
    def all_stats(self):
        return json.loads(self.stats) if self.stats else {}

    @property
    def technique_item_stat(self):
        return self.all_stats.get('technique', 0)

    @property
    def kicks_item_stat(self):
        return self.all_stats.get('kicks', 0)

    @property
    def ball_selection_item_stat(self):
        return self.all_stats.get('ball_selection', 0)

    @property
    def speed_item_stat(self):
        return self.all_stats.get('speed', 0)

    @property
    def endurance_item_stat(self):
        return self.all_stats.get('endurance', 0)

    @property
    def current_energy_item_stat(self):
        return self.all_stats.get('current_energy', 0)