from enum import Enum, auto
    
    
class VipPassPack:
    def __init__(self, duration, price):
        self.duration = duration
        self.price = price
        self.day_price = price / duration
        
class VipPassTypes(Enum):
    seven_days_pass = "seven_day_pass"
    month_pass = "month_pass" 

vip_passes = {
    VipPassTypes.seven_days_pass: VipPassPack(7, 149),
    VipPassTypes.month_pass: VipPassPack(30, 490)
}