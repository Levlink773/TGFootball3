from training.constans import STAT_RANGES, ENERGY_RANGES


def calculate_stat(score: int) -> int:
    for score_range, bonus in STAT_RANGES.items():
        if score in score_range:
            return bonus
    return 0

def calculate_energy(score: int) -> int:
    for score_range, bonus in ENERGY_RANGES.items():
        if score in score_range:
            return bonus
    return 0