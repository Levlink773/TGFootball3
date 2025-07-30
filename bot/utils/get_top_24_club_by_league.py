from datetime import datetime

from database.models.league_fight import LeagueFight

def get_top_24_clubs(fights: list[LeagueFight]) -> str:
    club_points = {}
    club_goals_scored = {}
    club_goals_conceded = {}

    for fight in fights:
        for club_id in [fight.first_club_id, fight.second_club_id]:
            if club_id not in club_points:
                club_points[club_id] = 0
                club_goals_scored[club_id] = 0
                club_goals_conceded[club_id] = 0

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

        if club.is_fake_club:
            continue 

        goals_scored = club_goals_scored[club_id]
        goals_conceded = club_goals_conceded[club_id]
        goal_difference = goals_scored - goals_conceded

        rankings.append({
            'club_id': club_id,
            'club_name': club.name_club,
            'points': points,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'goal_difference': goal_difference,
            'total_power': club.total_power,  
            'club': club 
        })
    sorted_rankings = sorted(rankings, key=lambda x: (-x['points'], -x['goal_difference'], -x['goals_scored']))
    return sorted_rankings