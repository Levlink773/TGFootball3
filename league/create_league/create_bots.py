
from database.models.club import Club
from database.models.user_bot import UserBot
from database.models.character import Character

from services import user_service,club_service, character_service
from services.club_infrastructure_service import ClubInfrastructureService
from constants import MAX_LEN_MEMBERS_CLUB, Gender, PositionCharacter

import random
cities = [
    "London", "Madrid", "Paris", "Berlin", "Rome", "Milan", "Lisbon", 
    "Amsterdam", "Brussels", "Vienna", "Prague", "Warsaw", "Dublin"
]
 
adjectives = [
    "United", "City", "FC", "Athletic", "Rovers", "Wanderers", 
    "Rangers", "Galaxy", "Royals", "Tigers", "Eagles"
]

animals = [
    "Lions", "Wolves", "Panthers", "Bears", "Dragons", "Eagles", 
    "Tigers", "Sharks", "Dolphins", "Hawks", "Falcons"
]

def generate_team_names(num_teams = 1):
    team_names = []
    for _ in range(num_teams):
        city = random.choice(cities)
        adjective = random.choice(adjectives)
        animal = random.choice(animals)
        team_name = f"{city} {adjective} {animal}"
        team_names.append(team_name)
    return team_names[0]

class BOTS:
    
    def __init__(self, average_club_strength: int, name_league: str) -> None:
        self.average_club_strength = average_club_strength
        self.name_league = name_league
    
    @property
    def random_user_id(self):
        return random.randint(1000,100000000)
    
    @property
    def random_user_name(self):
        return f"bot_{self.random_user_id}"
    
    async def __create_userbot(self) -> UserBot:    
        user_id = self.random_user_id
        await user_service.UserService.create_user(
            user_id        = user_id,
            user_name      = self.random_user_name,
            user_full_name = self.random_user_name 
        )
        return await user_service.UserService.get_user(
            user_id=user_id
        )
    
    async def __create_club(self, user: UserBot) -> Club:
        club =  await club_service.ClubService.create_club(
            name_club=generate_team_names(),
            owner_id=user.user_id,
            fake_club=True,
            league=self.name_league
            
        )
        await ClubInfrastructureService.create_infrastructure(
            club_id=club.id
        )
        return club
        
    async def __create_characters(self, club: Club, user: UserBot):
        
        average_power = int(self.average_club_strength / 5)  
        character_obj = Character(
            characters_user_id = user.user_id,
            name = self.random_user_name,
            technique = average_power + random.randint(1,5),
            kicks = average_power + random.randint(1,5),
            ball_selection = average_power + random.randint(1,5),
            speed = average_power + random.randint(1,5),
            endurance = average_power + random.randint(1,5) ,
            position = PositionCharacter.ATTACKER,
            gender = Gender.MAN,
            club_id = club.id,
            is_bot = True
        )
        return await character_service.CharacterService.create_character(
            character_obj
        )
            

        
    async def create_character(self, club: Club, user: UserBot):
        character = await self.__create_characters(
            club=club,
            user=user
        )
        await character_service.CharacterService.update_character_club_id(
            character=character,
            club_id=club.id
        )
        
    async def create_bot_clubs(self, len_bots_club: int) -> list[Club]:
        clubs = []
        update_clubs = []
        for _ in range(len_bots_club):
            user           = await self.__create_userbot()
            club           = await self.__create_club(user)
            await self.create_character(club, user)
            clubs.append(club)
            
        for club in clubs:
            club = await club_service.ClubService.get_club(
                    club_id=club.id
                                )
            update_clubs.append(club)
        return update_clubs