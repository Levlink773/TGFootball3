def get_base():
    from database.model_base import Base
    from database.models.user_bot import UserBot
    from database.models.character import Character
    from database.models.club import Club
    from database.models.league_fight import LeagueFight
    from database.models.item import Item
    from database.models.reminder_character import ReminderCharacter
    from database.models.duel import Duel
    from database.models.match_character import MatchCharacter
    from database.models.christmas_reward import ChristmasReward
    from database.models.payment.box_payment import BoxPayment
    from database.models.payment.vip_pass_payment import VipPassPayment
    from database.models.payment.energy_payment import EnergyPayment
    from database.models.payment.money_payment import MoneyPayment
    from database.models.payment.payments import Payment
    from database.models.training import TrainingTimer, CharacterJoinTraining
    from database.models.club_infrastructure import ClubInfrastructure
    
    return Base