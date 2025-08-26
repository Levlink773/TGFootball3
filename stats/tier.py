# --- Жёстко фиксируем порядок Tier-ов (важно для индексов в cipher) ---
import random
from typing import List

from stats.stat_enum import StatisticsType

TIER_LIST: List[tuple[str, List[StatisticsType]]] = [
    ("🔹 Tier 1", [
        StatisticsType.CONDUCT_3_TRAINING,
        StatisticsType.CONDUCT_5_TRAINING,
        StatisticsType.CONDUCT_7_TRAINING,
    ]),
    ("🔸 Tier 2", [
        StatisticsType.PLAY_BLITZ,              # если нужно именно "Прийняти участь у Бліц"
        StatisticsType.PLAY_2_BLITZ,
        StatisticsType.GOAL_IN_MATCH,
    ]),
    ("🔶 Tier 3", [
        StatisticsType.REGISTER_ON_MATCH,
        StatisticsType.MVP_TWO,
        StatisticsType.MVP_TWO_HALF,
        StatisticsType.MVP_THREE,
        StatisticsType.RICH_FINAL_WIN_BLITZ,
        StatisticsType.RICH_SEMI_FINAL_BLITZ,
    ]),
]

# ----------------- Cipher: "1,3,2" — 1-based индексы по TIER_LIST -----------------
def _encode_indices(indices: List[int]) -> str:
    return ",".join(str(max(1, i)) for i in indices)

def _decode_indices(s: str, tiers_count: int) -> List[int]:
    """
    Возвращает список длиной tiers_count, где каждый элемент — 1-based индекс задачи для соответствующего Tier.
    Любые некорректные значения приводим к допустимым.
    """
    if not s:
        return []
    parts = []
    for tok in s.split(","):
        tok = tok.strip()
        if not tok.isdigit():
            parts.append(1)
        else:
            parts.append(int(tok))
    # подгоняем длину под количество Tier-ов
    if len(parts) < tiers_count:
        parts += [1] * (tiers_count - len(parts))
    elif len(parts) > tiers_count:
        parts = parts[:tiers_count]
    return parts

def _generate_indices_for_all_tiers() -> List[int]:
    """
    Сгенерировать валидный список индексов (1-based) — по одному индексу на каждый Tier.
    """
    indices = []
    for _, stat_types in TIER_LIST:
        # 1..len(stat_types)
        indices.append(random.randint(1, max(1, len(stat_types))))
    return indices

def _safe_pick(stat_types: List[StatisticsType], one_based_index: int) -> StatisticsType:
    """
    Безопасно получить элемент по 1-based индексу. Выходит за границы — зажимаем.
    """
    if not stat_types:
        raise ValueError("Tier has no statistics configured")
    i = max(1, one_based_index)
    i = min(i, len(stat_types))
    return stat_types[i - 1]
# --------------------------------------------------------------------