from dataclasses import dataclass, field
import random

@dataclass
class ITEM:
    name: str
    chance: int
    min: int = 1
    max: int = 100
    step_count: int = 1
    count_item: int = field(init=False)
    description: str = ""

    def __post_init__(self):
        self.count_item = self.get_count()

    def get_count(self):
        return random.randrange(start=self.min, stop=self.max, step=self.step_count)



@dataclass
class Energy(ITEM):
    name: str = field(default = "⚡️ ")
    chance: int = field(default = 100)
    description: str = field(default = "Енергія")
    step_count: int = field(default = 5)
    
@dataclass
class Money(ITEM):
    name: str = field(default = "💰")
    chance: int = field(default = 100)
    description: str = field(default = "Монети")
    step_count: int = field(default = 1)

@dataclass
class Exp(ITEM):
    name: str = field(default = "🎓")
    chance: int = field(default = 100)
    description: str = field(default = "Досвід")
    step_count: int = field(default = 1)
