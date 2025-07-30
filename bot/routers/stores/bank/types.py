from enum import Enum, auto

class MoneyPack:
    def __init__(self, name, coins, price):
        self.name = name
        self.coins = coins
        self.price = price

    def __repr__(self):
        return f"{self.name}: {self.coins} монет - {self.price} грн"

class MoneyPackType(Enum):
    SMALL = "SMALL"  
    MIDDLE = "MIDDLE" 
    BIG = "BIG"  
    KING = "KING"   
    
money_packs = {
    MoneyPackType.SMALL: MoneyPack("Small pack", 100, 150),
    MoneyPackType.MIDDLE: MoneyPack("Middle pack", 250, 330),
    MoneyPackType.BIG: MoneyPack("Big pack", 500, 590),
    MoneyPackType.KING: MoneyPack("King pack", 1000, 990) 
}