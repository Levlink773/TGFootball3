import random

def check_chance(chance: int) -> bool:
    random_chance = random.random() * 100
    if random_chance  < chance:
        return True
    else:
        return False
    
