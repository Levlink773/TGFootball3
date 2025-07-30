from abc import ABC, abstractmethod

from database.models.character import Character
from database.models.club import Club

from services.club_service import ClubService
from services.league_services.top_20_club_league_service import Top20ClubLeagueService

from loader import bot
from utils.rate_limitter import rate_limiter

class SendInformationToClub(ABC):
    
    def __init__(self, clubs: list[Club]) -> None:
        self.clubs: list[Club] = clubs
    
    @abstractmethod
    async def send_info_to_clubs(self):
        pass
    
    @rate_limiter
    async def _send_message_to_character(
        self,
        character: Character,
        message: str
    ):
        try:
            if character.is_bot:
                return
            
            await bot.send_message(
                chat_id=character.characters_user_id,
                text=message
            )
        except Exception as E:
            pass

        
    @property
    def all_users(self) -> list[Character]:
        return [character for club in self.clubs for character in club.characters]



class SendEndMatch(SendInformationToClub):

    TEMPLATE = """
    🔥 Починається останній матч між двома клубами — <b>{team_1}</b> та <b>{team_2}</b>! ⚔️
    
    💥 Це два найсильніші та найстійкіші клуби, які довели свою міць протягом усього сезону! 💪
    
    {team_1} — команда, яка славиться своєю неймовірною атакуючою потужністю та безжалісною грою на полі. ⚡️ Їхня стратегія та командна робота не раз приводили їх до перемог у найнапруженіших матчах. 🏆
    
    {team_2}, своєю чергою, відомі своєю непохитною обороною та характером. 🛡️ Цей клуб завжди бореться до останнього, навіть коли здається, що сили на виході. ⚔️
    
    🎉 Сьогодні ми дізнаємось, хто з цих величних команд стане переможцем, хто забере титул і увічнить своє ім'я в історії! 📜 Все вирішиться тут і зараз! ⏳
    """

    def __init__(
        self, 
        clubs: list[Club],
        best_2_clubs: list[Club]
        ) -> None:
        self.best_2_clubs = best_2_clubs
        super().__init__(clubs)

    
    async def send_info_to_clubs(self):
        for character in self.all_users:
            await self._send_message_to_character(
                character=character,
                message=self.text_end_match
            )


    @property
    def text_end_match(self) -> str:
        return self.TEMPLATE.format(
            team_1=self.best_2_clubs[0].name_club,
            team_2=self.best_2_clubs[1].name_club
        )
        
class SendCongratulationEndMatch(SendInformationToClub):
    TEMPLATE = """
🎉🏆 ВІТАЄМО КОМАНДУ <b>{team_winner}</b> З ГРАНДІОЗНОЮ ПЕРЕМОГОЮ!🏆🎉

💥 Ви довели, що справжня міць і командний дух здатні творити дива на полі! 🌟 Сьогоднішній матч став справжнім тріумфом вашої наполегливості, майстерності та стратегічного генія. ⚽️💪

Ваші вболівальники пишаються вами, а цей тріумф увійде в історію як символ неперевершеності та волі до перемоги! 🙌🔥

🥂 Нехай цей успіх стане лише початком нових звершень і приводом для подальших перемог! 🚀

<b>{team_winner}</b> — ЧЕМПІОНИ! 👑
    """
    
    def __init__(self) -> None:
        clubs:list[Club] = []
        super().__init__(clubs)
        self.winner_club: Club = None
        
    async def get_winner_club(self):
        last_match = await Top20ClubLeagueService.get_end_match()
        if last_match.total_points_first_club > last_match.total_points_second_club:
            self.winner_club = last_match.first_club
        else:
            self.winner_club = last_match.second_club
            
    async def send_info_to_clubs(self):
        all_clubs = await ClubService.get_all_clubs()
        await self.get_winner_club()
        self.clubs = [club for club in all_clubs if not club.is_fake_club]
        
        for character in self.all_users:
            await self._send_message_to_character(
                character=character,
                message=self.text_end_match
            )
    
    @property
    def text_end_match(self) -> str:
        return self.TEMPLATE.format(
            team_winner = self.winner_club.name_club
        )