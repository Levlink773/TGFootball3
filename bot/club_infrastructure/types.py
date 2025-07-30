from enum import Enum
from typing import Literal

NameInfrastructureType = Literal[
    "training_base", "training_center", "premium_fond", 
    "stadium", "sports_medicine", "academy_talent"
]


class InfrastructureType(Enum):
    TRAINING_BASE   = "🏋‍♂Тренувальна база"
    TRAINING_CENTER = "📚Навчальний центр"
    PREMIUM_FOND    = "🏆Преміальний фонд"
    STADIUM         = "🏟Стадіон" 
    SPORTS_MEDICINE = "🏥Спортивна медицина"
    ACADEMY_TALENT  = "🌟Академія талантів"



class InfrastructureTyping:
    map_infrastructure: dict[NameInfrastructureType, "InfrastructureType"] = {
            "training_base": InfrastructureType.TRAINING_BASE,
            "training_center": InfrastructureType.TRAINING_CENTER,
            "premium_fond": InfrastructureType.PREMIUM_FOND,
            "stadium": InfrastructureType.STADIUM,
            "sports_medicine": InfrastructureType.SPORTS_MEDICINE,
            "academy_talent": InfrastructureType.ACADEMY_TALENT
        }


    @classmethod
    def get_type(cls, name_infrastructure: NameInfrastructureType) -> "InfrastructureType":
        return cls.map_infrastructure[name_infrastructure]

    @classmethod
    def get_name(cls, infrastructure_type: "InfrastructureType") -> NameInfrastructureType:
        for name, type in cls.map_infrastructure.items():
            if type == infrastructure_type:
                return name

class InfrastructureLevel(Enum):
    LEVEL_0 = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    
    def get_next_level(self) -> "InfrastructureLevel":
        if self.value == 5:
            raise Exception("Max level")
        
        return InfrastructureLevel(self.value + 1)