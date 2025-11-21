from database.models.club import Club
from database.models.league_fight import LeagueFight

# from league.process_match.club_fight import ClubMatchManager, ClubMatch
from datetime import datetime

from services.character_service import CharacterService
from services.league_service import LeagueFightService
from services.match_character_service import MatchCharacterService
from services.club_service  import ClubService
from services.league_services.default_league_service import DefaultLeagueService
from services.league_services.best_league_service import BestLeagueService
from services.league_services.top_20_club_league_service import Top20ClubLeagueService
from services.league_services.new_clubs_league_service import NewClubsLeagueService

from match.core.manager import ClubMatchManager
from match.entities import MatchData

from bot.routers.league.utils import get_characters_club_in_match


def get_future_matches_by_club(club: Club) -> list[MatchData]: 
    current_time = datetime.now()
    
    all_fights_club = ClubMatchManager.get_matches_by_club(
        club_id=club.id
    )
    return [match for match in all_fights_club if match.start_time > current_time]
    
    
async def get_text_league(club: Club):

    current_match = await DefaultLeagueService.get_next_league_fight_by_club(club_id=club.id)
    if not current_match:
        return "⚽️ Твоя ліга: <b>{name_league}</b>\n\nМатчів немає, відпочивайте".format(name_league = club.league)
    
    match_data = ClubMatchManager.get_match(match_id=current_match.match_id)
    if not match_data:
        return "⚽️ Твоя ліга: <b>{name_league}</b>\n\nМатчів немає, відпочивайте".format(name_league = club.league)
    enemy_match_club = match_data.get_opposite_club(club_id=club.id)
    enemy_club = await ClubService.get_club(enemy_match_club.club_id)
    
    

    characters_in_match = await get_characters_club_in_match(
        club_id  = club.id,
        match_id = current_match.match_id
    )

    enemy_characters_in_match = await get_characters_club_in_match(
        club_id  = enemy_club.id,
        match_id = current_match.match_id
    )
    
    text = """
⚽️ Твоя ліга: <b>{name_league}</b>

⚔️ <b>Наступний матч</b> ⚔️

🛑 <code>{first_name_club}</code> [{power_first_club:.2f}] ({count_characters_first_club}/11)
<b>VS</b>
✳️ <code>{second_name_club}</code> [{power_second_club:.2f}] ({count_characters_second_club}/11)

⏰ Час початку: <b>{time_fight}</b>
    """
    
    return text.format(
        name_league       = club.league,
        first_name_club   = club.name_club,
        second_name_club  = enemy_club.name_club,
        time_fight        = match_data.start_time.strftime("%d:%m:%Y - %H:%M"),
        power_first_club  = sum([character.full_power for character in characters_in_match]),
        power_second_club = sum([character.full_power for character in enemy_characters_in_match]),
        count_characters_first_club  = len(characters_in_match),
        count_characters_second_club = len(enemy_characters_in_match)
    )
    
    
async def get_text_league_devision(club: Club):

    current_match = await BestLeagueService.get_next_league_fight_by_club(club_id=club.id)
    if not current_match:
        return "⚽️ Твоя ліга: <b>{name_league}</b>\n\nМатчів немає, відпочивайте".format(name_league = club.league)
    
    match_data = ClubMatchManager.get_match(match_id=current_match.match_id)
    enemy_club_id = match_data.second_club_id if club.id != match_data.second_club_id else match_data.first_club_id 
    enemy_club = await ClubService.get_club(enemy_club_id)
    
    

    characters_in_match = await get_characters_club_in_match(
        club_id  = club.id,
        match_id = current_match.match_id
    )

    enemy_characters_in_match = await get_characters_club_in_match(
        club_id  = enemy_club.id,
        match_id = current_match.match_id
    )
    
    text = """
⚽️ Вітаємо вашу команду із тим, що ви потрапили в : <b>{name_division}</b>

⚔️ <b>Наступний матч</b> ⚔️

🛑 <code>{first_name_club}</code> [{power_first_club:.2f}] ({count_characters_first_club}/11)
<b>VS</b>
✳️ <code>{second_name_club}</code> [{power_second_club:.2f}] ({count_characters_second_club}/11)

⏰ Час початку: <b>{time_fight}</b>
    """
    
    return text.format(
        name_division     = match_data.group_id,
        first_name_club   = club.name_club,
        second_name_club  = enemy_club.name_club,
        time_fight        = match_data.start_time.strftime("%d:%m:%Y - %H:%M"),
        power_first_club  = sum([character.full_power for character in characters_in_match]),
        power_second_club = sum([character.full_power for character in enemy_characters_in_match]),
        count_characters_first_club  = len(characters_in_match),
        count_characters_second_club = len(enemy_characters_in_match)
    )
    

async def get_text_top_club_text(club: Club):

    current_match = await Top20ClubLeagueService.get_next_league_fight_by_club(club_id=club.id)
    if not current_match:
        return "⚽️ Твоя ліга: <b>{name_league}</b>\n\nМатчів немає, відпочивайте".format(name_league = club.league)
    
    match_data = ClubMatchManager.get_match(match_id=current_match.match_id)
    
    enemy_club_id = match_data.second_club_id if club.id != match_data.second_club_id else match_data.first_club_id 
    enemy_club = await ClubService.get_club(enemy_club_id)
    
    

    characters_in_match = await get_characters_club_in_match(
        club_id  = club.id,
        match_id = current_match.match_id
    )

    enemy_characters_in_match = await get_characters_club_in_match(
        club_id  = enemy_club.id,
        match_id = current_match.match_id
    )
    
    text = """
⚽️ Вітаємо вашу команду із тим, що ви в <b>Національному Кубку України</b>

⚔️ <b>Наступний матч</b> ⚔️

🛑 <code>{first_name_club}</code> [{power_first_club:.2f}] ({count_characters_first_club}/11)
<b>VS</b>
✳️ <code>{second_name_club}</code> [{power_second_club:.2f}] ({count_characters_second_club}/11)

⏰ Час початку: <b>{time_fight}</b>
    """
    
    return text.format(
        name_division     = match_data.group_id,
        first_name_club   = club.name_club,
        second_name_club  = enemy_club.name_club,
        time_fight        = match_data.start_time.strftime("%d:%m:%Y - %H:%M"),
        power_first_club  = sum([character.full_power for character in characters_in_match]),
        power_second_club = sum([character.full_power for character in enemy_characters_in_match]),
        count_characters_first_club  = len(characters_in_match),
        count_characters_second_club = len(enemy_characters_in_match)
    )
     

def get_text_calendar_matches(matches: list[LeagueFight], club_id: int):
    sorted_fights: list[LeagueFight] = sorted(matches, key=lambda fight: fight.time_to_start)

    schedule_table = "📅 <b>Розклад матчів</b>\n\n"
    
    current_time = datetime.now()
    next_match_index = None

    for index, fight in enumerate(sorted_fights, start=1):
        if fight.first_club_id == club_id:
            my_club = fight.first_club
            opponent_club = fight.second_club
        else:
            my_club = fight.second_club
            opponent_club = fight.first_club
        
        if fight.time_to_start < current_time:
            match_status = "♟ Матч пройшов"
        else:
            match_status = "📍 Скоро буде"
            if next_match_index is None:
                next_match_index = index
                match_status = "🧤 Скоро буде"
        
        schedule_table += (
            f"{index}- тур. <b>{my_club.name_club}</b> vs <b>{opponent_club.name_club}</b>\n"
            f"🕒 Час початку: {fight.time_to_start.strftime('%d.%m.%Y %H:%M')}\n"
            f"<code>{match_status}</code>\n\n"
        )
    
    return schedule_table


def get_text_result(fights: list[LeagueFight], club_id: int):
    current_time = datetime.now()

    filtered_fights = [fight for fight in fights if fight.time_to_start < current_time]
    sorted_fights:list[LeagueFight] = sorted(filtered_fights, key=lambda fight: fight.time_to_start)

    schedule_table = "📅 <b>Результати матчей</b>\n\n"
    
    for index, fight in enumerate(sorted_fights, start=1):
        if fight.first_club_id == club_id:
            my_club = fight.first_club
            opponent_club = fight.second_club
            my_score = fight.goal_first_club
            opponent_score = fight.goal_second_club
        else:
            my_club = fight.second_club
            opponent_club = fight.first_club
            my_score = fight.goal_second_club
            opponent_score = fight.goal_first_club
        
        # Определяем результат
        if my_score > opponent_score:
            result = "Перемога"
        elif my_score < opponent_score:
            result = "Поразка"
        else:
            result = "Нічия"
        
        schedule_table += (
            f"{index}-тур. <b>{my_club.name_club}</b> vs <b>{opponent_club.name_club}</b>\n"
            f"⚽ Рахунок: {my_score} : {opponent_score}\n"
            f"📊 Результат: {result}\n\n"
        )
    
    return schedule_table

async def get_text_rating(fights: list[LeagueFight]):
    # Словари для подсчета очков, голов забитых, пропущенных и разницы голов
    club_points = {}
    club_goals_scored = {}
    club_goals_conceded = {}

    for fight in fights:
        if fight.first_club_id not in club_points:
            club_points[fight.first_club_id] = 0
            club_goals_scored[fight.first_club_id] = 0
            club_goals_conceded[fight.first_club_id] = 0
        if fight.second_club_id not in club_points:
            club_points[fight.second_club_id] = 0
            club_goals_scored[fight.second_club_id] = 0
            club_goals_conceded[fight.second_club_id] = 0
        
        if fight.time_to_start <= datetime.now():
            club_points[fight.first_club_id] += fight.total_points_first_club
            club_goals_scored[fight.first_club_id] += fight.goal_first_club
            club_goals_conceded[fight.first_club_id] += fight.goal_second_club
            
            club_points[fight.second_club_id] += fight.total_points_second_club
            club_goals_scored[fight.second_club_id] += fight.goal_second_club
            club_goals_conceded[fight.second_club_id] += fight.goal_first_club

    rankings = []
    for club_id, points in club_points.items():
        club = next(fight.first_club if fight.first_club_id == club_id else fight.second_club
                    for fight in fights if fight.first_club_id == club_id or fight.second_club_id == club_id)
        
        goals_scored = club_goals_scored[club_id]
        goals_conceded = club_goals_conceded[club_id]
        goal_difference = goals_scored - goals_conceded

        rankings.append({
            'club_id': club_id,  # Добавляем club_id
            'club_name': club.name_club,
            'points': points,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'goal_difference': goal_difference
        })

    sorted_rankings = sorted(rankings, key=lambda x: (-x['points'], -x['goal_difference'], -x['goals_scored']))

    ranking_table = "🏆 <b>Таблиця Рейтингів</b>\n\n"
    medals = ["🥇", "🥈", "🥉"]
    for index, rank in enumerate(sorted_rankings, start=1):
        club = await ClubService.get_club(
            club_id=rank['club_id']
        )
        medal = medals[index-1] if index <= 3 else f"{index}."
        club_info = f"<b>{rank['club_name']}</b>"
        
        ranking_table += (
            f"{medal} {club_info} <b>[{club.total_power:.2f}]</b>\n"
            f"Очки: {rank['points']}, ГЗ {rank['goals_scored']}; ГП {rank['goals_conceded']}, "
            f"РГ {'+' if rank['goal_difference'] >= 0 else ''}{rank['goal_difference']}\n\n"
            
        )
    
    return ranking_table


async def count_energy_characters_in_match(match_id, my_club_id:str):
    all_characters_in_match = await MatchCharacterService.get_characters_from_match(
            match_id=match_id
        )

    power_character = 0
    for character_in_match in all_characters_in_match:
        
        if character_in_match.club_id != my_club_id:
            continue
        
        character = await CharacterService.get_character_by_id(character_in_match.character_id)
        power_character += character.full_power
        
    return power_character

async def get_text_new_club_league(club: Club):

    current_match = await NewClubsLeagueService.get_next_league_fight_by_club(club_id=club.id)
    if not current_match:
        return "⚽️ Твоя ліга: <b>{name_league}</b>\n\nМатчів немає, відпочивайте".format(name_league = club.league)
    
    match_data = ClubMatchManager.get_match(match_id=current_match.match_id)
    
    enemy_club_id = match_data.second_club_id if club.id != match_data.second_club_id else match_data.first_club_id 
    enemy_club = await ClubService.get_club(enemy_club_id)
    
    

    characters_in_match = await get_characters_club_in_match(
        club_id  = club.id,
        match_id = current_match.match_id
    )

    enemy_characters_in_match = await get_characters_club_in_match(
        club_id  = enemy_club.id,
        match_id = current_match.match_id
    )
    
    text = """
⚽️ Вітаємо вашу команду із тим, що ви в <b>Лиги для новачків</b>

⚔️ <b>Наступний матч</b> ⚔️

🛑 <code>{first_name_club}</code> [{power_first_club:.2f}] ({count_characters_first_club}/11)
<b>VS</b>
✳️ <code>{second_name_club}</code> [{power_second_club:.2f}] ({count_characters_second_club}/11)

⏰ Час початку: <b>{time_fight}</b>
    """
    
    return text.format(
        name_division     = match_data.group_id,
        first_name_club   = club.name_club,
        second_name_club  = enemy_club.name_club,
        time_fight        = match_data.start_time.strftime("%d:%m:%Y - %H:%M"),
        power_first_club  = sum([character.full_power for character in characters_in_match]),
        power_second_club = sum([character.full_power for character in enemy_characters_in_match]),
        count_characters_first_club  = len(characters_in_match),
        count_characters_second_club = len(enemy_characters_in_match)
    )

def get_energy_multiplier(level: int) -> float:
    """Повертає множник енергії для заданого рівня.
       Для рівнів 1..5 використовує явний мапінг.
       Для level > 5 продовжує прогресію +0.1 на кожний додатковий рівень.
    """
    if level < 1:
        level = 1

    base_map = {
        1: 1.0,
        2: 1.1,
        3: 1.3,
        4: 1.4,
        5: 1.5,
    }

    if level in base_map:
        return base_map[level]

    # Продовження прогресії: від рівня 5 додаємо +0.1 за кожний рівень
    extra_levels = level - 5
    return base_map[5] + 0.1 * extra_levels