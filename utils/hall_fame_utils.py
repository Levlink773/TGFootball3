from collections import defaultdict

from bot.utils.get_top_24_club_by_league import get_top_24_clubs

from database.models.character import Character
from database.models.club import Club
from database.models.match_character import MatchCharacter
from database.models.duel import Duel
from database.models.league_fight import LeagueFight

from services.character_service import CharacterService

from services.league_services.default_league_service import DefaultLeagueService
from services.league_services.top_20_club_league_service import Top20ClubLeagueService

from constants import PositionCharacter 

def generate_rankings(entities, my_entity, entity_type, sorting_attribute, display_attribute, ranking_label):
    sorted_entities = sorted(entities, key=lambda entity: getattr(entity, sorting_attribute), reverse=True)

    rankings = []
    for index, entity in enumerate(sorted_entities[:15]):
        rank_icon = "🥇" if index == 0 else "🥈" if index == 1 else "🥉" if index == 2 else "⚔️"

        entity_name = ""
        display_value = 0
        display_format = "{:>5.2f}"  

        if entity_type == 'character':
            entity_name = entity.character_name
            display_value = getattr(entity, display_attribute)
            if display_attribute == 'level':
                display_format = "{:>5}"  
        elif entity_type == 'club':
            entity_name = entity.name_club
            display_value = getattr(entity, display_attribute)

        rankings.append(f"{index + 1:>2}. {entity_name:<15} - {display_format.format(display_value)} {ranking_label} {rank_icon}")
        
    if entity_type == 'character':
        entity_type_label = "персонажів"
    else:
        entity_type_label = "команд"

    top_15_header = f"Топ-15 найкращих {entity_type_label} за {ranking_label} 💪\n\n"
    top_15_text = top_15_header + "\n".join(rankings)

    my_entity_id = getattr(my_entity, 'characters_user_id' if entity_type == 'character' else 'id')
    current_entity = next((entity for entity in sorted_entities if getattr(entity, 'characters_user_id' if entity_type == 'character' else 'id') == my_entity_id), None)

    if current_entity:
        position = sorted_entities.index(current_entity) + 1
        top_15_text += f"\n\nТи посідаєш {position} місце 🏆"


    return f"{top_15_text}"

def get_top_characters_by_power(all_characters: list[Character], my_character: Character) -> str:
    return generate_rankings(all_characters, my_character, 'character', 'full_power', 'full_power', 'силою')


def get_top_characters_by_level(all_characters: list[Character], my_character: Character) -> str:
    return generate_rankings(all_characters, my_character, 'character', 'exp', 'level', 'рівня')


def get_top_club_by_power(all_clubs: list[Club], my_club: Club) -> str:
    return generate_rankings(all_clubs, my_club, 'club', 'total_power', 'total_power', 'силою')


async def get_top_bomber_rating(all_matches: list[MatchCharacter], my_character: Character):
    total_goals_by_character = defaultdict(int)
    
    for match in all_matches:
        total_goals_by_character[match.character_id] += match.goals_count
    
    sorted_characters = sorted(total_goals_by_character.items(), key=lambda item: item[1], reverse=True)
    rankings = []
    
    all_real_characters = []
    
    index = 0
    for character_id, total_goals in sorted_characters:
        character = await CharacterService.get_character_by_id(character_id)
        if character.is_bot:
            continue
        rank_icon = "🥇" if index == 0 else "🥈" if index == 1 else "🥉" if index == 2 else "⚔️"
        rankings.append(f"{index + 1:>2}. <b>{character.character_name:<10}</b> - {total_goals:>5} забитих голів {rank_icon}")
        
        all_real_characters.append(character)
        index += 1
        
    top_15_header = f"Топ-15 бомбардирів за забитими голами ⚽\n\n"
    top_15_text = top_15_header + "\n".join(rankings[:15])

    my_character_id = my_character.id
    my_total_goals = total_goals_by_character.get(my_character_id, 0)
    
    if my_character_id in total_goals_by_character:
        position = [i for i, character in enumerate(all_real_characters) if character.id == my_character_id][0] + 1
        top_15_text += f"\n\nТи посідаєш {position} місце з {my_total_goals} голами 🏆"

    return top_15_text

def get_top_duelists_ranking(all_duels: list[Duel], my_character: Character):
    total_points_by_character = defaultdict(int)
    characters_dict = {}

    # Подсчет очков за каждый дуэль и сбор информации о персонажах
    for duel in all_duels:
        characters_dict[duel.user_1.id] = duel.user_1.character_name
        characters_dict[duel.user_2.id] = duel.user_2.character_name
        
        if duel.get_winner_duel == [duel.user_1, duel.user_2]:
            # Ничья, каждому игроку по 1 очку
            total_points_by_character[duel.user_1.id] += 1
            total_points_by_character[duel.user_2.id] += 1
        else:
            # Победитель получает 3 очка
            winner = duel.get_winner_duel
            loser = duel.user_1 if winner == duel.user_2 else duel.user_2
            total_points_by_character[winner.id] += 3
            total_points_by_character[loser.id] += 0  # проигравший не получает очков

    # Преобразование словаря в список кортежей (id персонажа, очки)
    sorted_characters = sorted(total_points_by_character.items(), key=lambda item: item[1], reverse=True)

    rankings = []

    index = 0
    for character_id, total_points in sorted_characters[:15]:
        # Используем имя персонажа из дуэлей
        character_name = characters_dict.get(character_id, "Unknown")
        rank_icon = "🥇" if index == 0 else "🥈" if index == 1 else "🥉" if index == 2 else "⚔️"
        rankings.append(f"{index + 1:>2}. <b>{character_name:<10}</b> - {total_points:>5} очков {rank_icon}")
        index += 1
    
    top_15_header = f"Топ-15 дуелянтів за очками ⚔️\n\n"
    top_15_text = top_15_header + "\n".join(rankings)

    # Проверяем, есть ли персонаж среди тех, чьи очки были учтены
    my_character_id = my_character.id
    my_total_points = total_points_by_character.get(my_character_id, 0)
    
    if my_character_id in total_points_by_character:
        # Определение позиции пользователя на основе его ID
        position = [i for i, (char_id, _) in enumerate(sorted_characters) if char_id == my_character_id][0] + 1
        top_15_text += f"\n\nТи займаєш {position} місце з {my_total_points} очками 🏆"
    else:
        top_15_text += f"\n\nТи не увійшов у топ-15, але у тебе {my_total_points} очок 🏅"

    return top_15_text


async def get_top_24_clubs_text() -> str:
    default_fights = await DefaultLeagueService.get_month_league()
    sorted_rankings_defaule = get_top_24_clubs(default_fights)
    top_20_club_fights = await Top20ClubLeagueService.get_month_league()
    sorted_rankings_top_20 = get_top_24_clubs(top_20_club_fights)

    all_clubs = sorted_rankings_top_20 + sorted_rankings_defaule
    club_data = defaultdict(lambda: {
        'club': None,
        'club_id': 0,
        'club_name': '',
        'points': 0,
        'goals_scored': 0,
        'goals_conceded': 0,
        'goal_difference': 0,
        'total_power': 0,
    })

    for entry in all_clubs:
        club_id = entry['club_id']
        data = club_data[club_id]

        if data['club'] is None:
            data['club'] = entry['club']
            data['club_id'] = club_id
            data['club_name'] = entry['club_name']
            data['total_power'] = entry['total_power']

        data['points'] += entry['points']
        data['goals_scored'] += entry['goals_scored']
        data['goals_conceded'] += entry['goals_conceded']
        data['goal_difference'] += entry['goal_difference']
    sorted_rankings = dict(
        sorted(club_data.items(), key=lambda item: item[1]['points'], reverse=True)
    )
    sorted_rankings = [club for _, club in sorted_rankings.items()]
    champions_league = sorted_rankings[:8]
    europa_league = sorted_rankings[8:16]
    conference_league = sorted_rankings[16:24]

    def format_league_section(league, title, emoji):
        return f"{title}\n" + "\n".join(
            f"<b>{index + 1}.</b> {rank['club_name']} {emoji} [💪 {rank['total_power']:.2f}] "
            f"[ОЧ {rank['points']}], "
            f"[РГ {'+' if rank['goal_difference'] >= 0 else ''}{rank['goal_difference']}]"
            for index, rank in enumerate(league)
        ) + "\n\n"

    ranking_table = "🏆 <b>Рейтинг команд</b>\n\n"
    ranking_table += format_league_section(champions_league, "<b><u>Ліга Чемпіонів</u></b>\n", "🏆")
    ranking_table += format_league_section(europa_league, "<b><u>Ліга Європи</u></b>\n", "⚽️")
    ranking_table += format_league_section(conference_league, "<b><u>Ліга Конференції</u></b>\n", "🌟")

    return ranking_table


def get_top_characters_by_position(
    all_characters: list[Character], 
    my_character: Character, 
    position: PositionCharacter
) -> str:
    characters_by_position = [char for char in all_characters if char.position_enum == position]
    
    sorted_characters = sorted(characters_by_position, key=lambda char: char.full_power, reverse=True)
    
    rankings = []
    for index, char in enumerate(sorted_characters[:15]):
        rank_icon = "🥇" if index == 0 else "🥈" if index == 1 else "🥉" if index == 2 else "⚔️"
        rankings.append(f"{index + 1:>2}. <b>{char.character_name:<10}</b> - {char.full_power:>5.2f} силою {rank_icon}")
    
    top_15_header = f"Топ-15 персонажів на позиції {position.value} за силою 💪\n\n"
    top_15_text = top_15_header + "\n".join(rankings)
    
    if my_character.position_enum == position:
        my_character_id = my_character.id
        my_position = next((i for i, char in enumerate(sorted_characters) if char.id == my_character_id), None)
        if my_position is not None:
            top_15_text += f"\n\nТи посідаєш {my_position + 1} місце 🏆"
    
    return top_15_text


async def get_top_mvp_users_ranking(active_users: list[MatchCharacter], my_character: Character) -> str:
    total_scores_by_character = defaultdict(int)

    for user in active_users:
        total_scores_by_character[user.character_id] += user.count_score

    sorted_characters = sorted(total_scores_by_character.items(), key=lambda item: item[1], reverse=True)

    rankings = []
    index = 0
    my_position = None

    top_15_real_characters = []

    for i, (character_id, total_score) in enumerate(sorted_characters):
        character = await CharacterService.get_character_by_id(character_id)
        if character.is_bot:
            continue

        if index < 15:
            rank_icon = "🥇" if index == 0 else "🥈" if index == 1 else "🥉" if index == 2 else "⚔️"
            rankings.append(f"{index + 1:>2}. <b>{character.character_name:<10}</b> - {total_score:>5} очков {rank_icon}")
            top_15_real_characters.append(character)

        if character.id == my_character.id:
            my_position = index + 1  # Позиция в общем реальном списке

        index += 1

    top_15_header = "Топ-15 MVP гравців⚽\n\n"
    top_15_text = top_15_header + "\n".join(rankings)

    my_total_score = total_scores_by_character.get(my_character.id, 0)

    if my_position:
        top_15_text += f"\n\nТи посідаєш {my_position} місце з {my_total_score} очками 🏆"
    else:
        top_15_text += f"\n\nТебе немає в топ-15. Ти набрав {my_total_score} очок 🏆"

    return top_15_text