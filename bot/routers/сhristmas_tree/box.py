from bot.boxes.base_box import Box
from bot.boxes.base_item import Energy, Money

cristmas_box = Box(
    items = [
        Energy(
            min = 10,
            max = 50
        )
        ,
        Money(
            min=5,
            max = 10
        )
    ]
)

