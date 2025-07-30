from .types import InfrastructureType, InfrastructureLevel
from .config import INFRASTRUCTURE_BONUSES, UPGRADE_COSTS

DESCRIPTION_TEMPLATE = """
<b>{name}</b>
{description}

<b>📊 Поточний рівень: {current_level}/{max_level}</b>
🔹 {effect}: {current_bonus}%
"""

NEXT_LEVEL_TEMPLATE_OWNER = """
🆙 <b>Наступний рівень ({next_level}/{max_level}):</b>  
🔸 {effect} +{next_bonus}%  
💰 Покращення коштує: {upgrade_cost}
"""

NEXT_LEVEL_TEMPLATE_NON_OWNER = """
🆙 <b>Наступний рівень ({next_level}/{max_level}):</b>  
🔸 {effect} +{next_bonus}%
"""

def get_description_infrastructure(
    infrastructure_type: InfrastructureType, 
    infrastructure_level: InfrastructureLevel, 
    is_owner: bool
) -> str:
    infra = infrastructure_info[infrastructure_type]
    current_bonus = INFRASTRUCTURE_BONUSES[infrastructure_type].get(infrastructure_level)

    max_level: int = len(InfrastructureLevel) - 1
    next_level: InfrastructureLevel = InfrastructureLevel(infrastructure_level.value + 1) if infrastructure_level.value != max_level else None
    next_bonus = INFRASTRUCTURE_BONUSES[infrastructure_type].get(next_level) if next_level else None

    upgrade_cost = UPGRADE_COSTS.get(next_level, "-") if next_level else None

    text = DESCRIPTION_TEMPLATE.format(
        name=infra["name"],
        description=infra["description"],
        current_level=infrastructure_level.value,
        max_level=max_level,
        effect=infra["effect"],
        current_bonus=current_bonus
    )

    if next_level:
        next_level_template = NEXT_LEVEL_TEMPLATE_OWNER if is_owner else NEXT_LEVEL_TEMPLATE_NON_OWNER
        text += next_level_template.format(
            next_level=next_level.value,
            max_level=max_level,
            effect=infra["effect"],
            next_bonus=next_bonus,
            upgrade_cost=upgrade_cost
        )

    return text.strip()
    
    
infrastructure_info = {
    InfrastructureType.TRAINING_BASE : {
        "name": "🏋‍♂ Тренувальна база",
        "description": "Сучасне обладнання та кваліфіковані тренери допомагають гравцям розвивати фізичну форму та навички.",
        "effect": "Збільшує шанс успішного тренування."
    },
    InfrastructureType.TRAINING_CENTER: {
        "name": "📚 Навчальний центр",
        "description": "Система підготовки гравців, що дозволяє їм покращувати розуміння тактики та стратегій гри.",
        "effect": "Збільшує нагороди за навчання гравців."
    },
    InfrastructureType.PREMIUM_FOND: {
        "name": "🏆 Преміальний фонд",
        "description": "Призові виплати за перемоги мотивують команду на досягнення кращих результатів.",
        "effect": "Збільшує нагороди за перемоги в матчах."
    },
    InfrastructureType.STADIUM: {
        "name": "🏟 Стадіон",
        "description": "Сучасний стадіон з розвиненою інфраструктурою приваблює більше вболівальників та збільшує доходи клубу.",
        "effect": "Збільшує коефіцієнт доната в гол."
    },
    InfrastructureType.SPORTS_MEDICINE: {
        "name": "🏥 Спортивна медицина",
        "description": "Покращені методи реабілітації та відновлення дозволяють гравцям швидше відновлювати сили.",
        "effect": "Зменшує час між тренуваннями."
    },
    InfrastructureType.ACADEMY_TALENT: {
        "name": "🌟 Академія талантів",
        "description": "Програма розвитку молодих гравців допомагає знаходити нові зірки для команди.",
        "effect": "Збільшує базову силу команди в матчах."
    }
}
