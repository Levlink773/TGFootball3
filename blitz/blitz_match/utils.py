import hashlib

from .constans import (
    MIN_DONATE_ENERGY_TO_BONUS_KOEF,
    KOEF_DONATE_ENERGY,
    BASE_KOEF_ADD_POWER
)


def calculate_bonus_from_count_characters(
    len_characters: int,
    power: int
) -> int:
    ranges = {
        (0, 2): 0,
        (5, 6): 5,
        (7, 9): 7,
        (10, 11): 10
    }

    bonus_procent = 0

    for (low, high), value in ranges.items():
        if low <= len_characters <= high:
            bonus_procent = value
            break
    
    return power * (bonus_procent / 100)
    
def calculate_bonus_donate_energy(
    donate_energy: int,
    power_club: int,
    power_opponent_club: int,    
) -> int:
    
    if donate_energy >= MIN_DONATE_ENERGY_TO_BONUS_KOEF:
        donate_energy = donate_energy + (donate_energy * ((donate_energy * KOEF_DONATE_ENERGY)/100))
    percent = donate_energy * BASE_KOEF_ADD_POWER
    total_power = power_club + power_opponent_club
    return percent * (total_power / 100)

def generate_blitz_match_id(team1_id: int, team2_id: int) -> str:
    sorted_ids = sorted([team1_id, team2_id])
    combined = f"{sorted_ids[0]}-{sorted_ids[1]}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]  # сокращённый hash
