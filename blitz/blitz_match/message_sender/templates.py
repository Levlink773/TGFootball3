from enum import Enum

from .types import SceneTemplate
from ..entities import BlitzMatchData

# --- СЦЕНИ БЕЗ ГОЛА (NO_GOAL_EVENT_SCENES) ---
# Списки розширено, щоб для кожної комбінації було мінімум 3 варіанти.
NO_GOAL_EVENT_SCENES = [
    # --- Roles: ["team_character", "enemy_team_character"] ---
    SceneTemplate(
        text="<b>{team_character}</b> б'є впритул, але <b>{enemy_team_character}</b> у шпагаті блокує цей удар! Неймовірний захист! 🧱🔥",
        required_positions=["team_character", "enemy_team_character"]
    ),
    SceneTemplate(
        text="Удар зльоту від <b>{team_character}</b>! Але <b>{enemy_team_character}</b> кидається під м'яч і рятує команду. Це самопожертва! 💥🛡️",
        required_positions=["team_character", "enemy_team_character"]
    ),
    SceneTemplate(
        text="Небезпечний простріл на <b>{team_character}</b>, але <b>{enemy_team_character}</b> в останню мить вибиває м'яч з-під ніг. Ледь не проскочило! ⚡️",
        required_positions=["team_character", "enemy_team_character"]
    ),
    SceneTemplate(
        text="<b>{team_character}</b> вже замахнувся на удар, але <b>{enemy_team_character}</b> встигає підкотитися і вибити м’яч. Героєм матчу може стати! 🦸",
        required_positions=["team_character", "enemy_team_character"]
    ),
    SceneTemplate(
        text="Після розкішного пасу <b>{team_character}</b> виходить на ударну позицію, але <b>{enemy_team_character}</b> чудово читає гру і перехоплює м’яч! 🧠",
        required_positions=["team_character", "enemy_team_character"]
    ),
    SceneTemplate(
        text="<b>{team_character}</b> пробиває у верхній кут, але <b>{enemy_team_character}</b> витягує цей м’яч з-під поперечини! Фантастичний сейв! 🧤😮",
        required_positions=["team_character", "enemy_team_character"]
    ),
    SceneTemplate(
        text="<b>{team_character}</b> виривається сам на сам, але <b>{enemy_team_character}</b> кидається в ноги і рятує ситуацію! Блискавична реакція! ⚡️🧤",
        required_positions=["team_character", "enemy_team_character"]
    ),
    SceneTemplate(
        text="Момент для <b>{team_character}</b>! Удар — але <b>{enemy_team_character}</b> на лінії воріт виносить м’яч! Просто неймовірно! 🚫🥅",
        required_positions=["team_character", "enemy_team_character"]
    ),
    SceneTemplate(
        text="<b>{team_character}</b> намагається обійти <b>{enemy_team_character}</b> і пробити, але той не дозволяє цього, виграючи мікродуель. 🥊",
        required_positions=["team_character", "enemy_team_character"]
    ),
    SceneTemplate(
        text="Блискуча передача на <b>{team_character}</b> і здається, що це гол! Але <b>{enemy_team_character}</b> встигає підставити ногу! Шанс втрачено! ❌",
        required_positions=["team_character", "enemy_team_character"]
    ),
    # --- Roles: ["team_character"] ---
    SceneTemplate(
        text="<b>{team_character}</b> обігрує всіх і вже б'є по воротах, але м’яч влучає у штангу і вилітає за межі поля! Який момент! 😱🥅",
        required_positions=["team_character"]
    ),
    SceneTemplate(
        text="<b>{team_character}</b> пробиває в дотик після класної передачі, але м’яч просвистів поруч зі стійкою. Лічені сантиметри! 🌀",
        required_positions=["team_character"]
    ),
    SceneTemplate(
        text="<b>{team_character}</b> виривається сам на сам і вже готовий забивати, але підслизнувся в останню мить! Невдача! ❄️🤦",
        required_positions=["team_character"]
    ),
    SceneTemplate(
        text="Після індивідуального проходу <b>{team_character}</b> потужно б'є — і м’яч з гуркотом влучає в поперечину! Глядачі схопилися за голови! 😵‍💫",
        required_positions=["team_character"]
    ),
    SceneTemplate(
        text="<b>{team_character}</b> опиняється у вигідній позиції, б’є... але м’яч проходить вище воріт! Такий шанс не кожного дня! 🎯",
        required_positions=["team_character"]
    ),

]

# --- ГОЛЕВЫЕ СЦЕНЫ (GOAL_EVENT_SCENES) ---
# Списки розширено, щоб для кожної комбінації було мінімум 3 варіанти.
GOAL_EVENT_SCENES = [
    # --- Roles: ["assistant", "scorer"] ---
    SceneTemplate(
        text="<b>{assistant}</b> і <b>{scorer}</b> розіграли блискучу стіночку, після якої <b>{scorer}</b> спокійно відправив м'яч у сітку! Ідеальна взаємодія! 🤝⚽️",
        required_positions=["assistant", "scorer"]
    ),
    SceneTemplate(
        text="<b>{assistant}</b> протягнув м'яч флангом і віддав ідеальний пас на <b>{scorer}</b>, якому залишалося лише підставити ногу! ГОЛ! 🔥🎯",
        required_positions=["assistant", "scorer"]
    ),
    SceneTemplate(
        text="Яка комбінація! <b>{assistant}</b> віддає пас п'ятою, а <b>{scorer}</b> в дотик відправляє м'яч у ворота! Це було красиво! 🤩",
        required_positions=["assistant", "scorer"]
    ),

    # --- Roles: ["assistant", "scorer", "enemy_goalkeeper"] ---
    SceneTemplate(
        text="<b>{assistant}</b> перехоплює м'яч, миттєвий пас на <b>{scorer}</b> — і той потужним ударом прошиває <b>{enemy_team_character}</b>! ⚡️🥅",
        required_positions=["assistant", "scorer", "enemy_team_character"]
    ),
    SceneTemplate(
        text="<b>{assistant}</b> навішує у штрафний майданчик, <b>{scorer}</b> виграє верхову боротьбу і головою б'є повз <b>{enemy_team_character}</b>! 🧠",
        required_positions=["assistant", "scorer", "enemy_team_character"]
    ),
    SceneTemplate(
        text="<b>{assistant}</b> виводить <b>{scorer}</b> віч-на-віч, і той холоднокровно переграє <b>{enemy_team_character}</b>! Класика! ❄️",
        required_positions=["assistant", "scorer", "enemy_team_character"]
    ),

    # --- Roles: ["scorer", "enemy_defender"] ---
    SceneTemplate(
        text="<b>{scorer}</b> накрутив <b>{enemy_team_character}</b> фінтами і невідпорно пробив у дальній кут! Майстерний гол! 🎩✨",
        required_positions=["scorer", "enemy_team_character"]
    ),
    SceneTemplate(
        text="<b>{scorer}</b> ставить корпус, відтісняє <b>{enemy_team_character}</b> і з розвороту б'є точно в ціль! Силовий гол! 💪",
        required_positions=["scorer", "enemy_team_character"]
    ),
    SceneTemplate(
        text="<b>{enemy_team_character}</b> намагається перехопити м'яч, але <b>{scorer}</b> виявляється спритнішим і з-під захисника відправляє м'яч у сітку! ⚡️",
        required_positions=["scorer", "enemy_team_character"]
    ),

    # --- Roles: ["assistant", "scorer", "enemy_team_character"] ---
    SceneTemplate(
        text="<b>{assistant}</b> віддає пас у розріз, <b>{scorer}</b> випереджає <b>{enemy_team_character}</b> і холоднокровно реалізує свій момент! 🚀",
        required_positions=["assistant", "scorer", "enemy_team_character"]
    ),
    SceneTemplate(
        text="<b>{assistant}</b> прокидає м'яч поміж ніг <b>{enemy_team_character}</b>, а <b>{scorer}</b> вже чекає на передачу і забиває! Ефектно! 🤯",
        required_positions=["assistant", "scorer", "enemy_team_character"]
    ),
    SceneTemplate(
        text="<b>{scorer}</b> отримує пас від <b>{assistant}</b>, і навіть відчайдушний підкат від <b>{enemy_team_character}</b> не рятує команду від голу! 💥",
        required_positions=["assistant", "scorer", "enemy_team_character"]
    ),

    # --- Roles: ["scorer"] ---
    SceneTemplate(
        text="<b>{scorer}</b> наважується на удар з дальньої дистанції — і м'яч залітає точнісінько в дев'ятку! Неймовірний постріл! 💣💥",
        required_positions=["scorer"]
    ),
    SceneTemplate(
        text="<b>{scorer}</b> підхоплює м'яч після рикошету, миттєво оцінює ситуацію і влучним ударом забиває гол! Гольове чуття! 🎯",
        required_positions=["scorer"]
    ),
    SceneTemplate(
        text="<b>{scorer}</b> бере ініціативу на себе, йде в сольний прохід і завершує його ідеальним ударом! Все зробив сам! 🦁",
        required_positions=["scorer"]
    ),

    # --- Roles: ["scorer", "enemy_team_character"] ---
    SceneTemplate(
        text="<b>{scorer}</b> підхоплює м'яч, на швидкості обходить захисника і б'є повз <b>{enemy_team_character}</b>! Сольний прохід, що завершився голом! 💪",
        required_positions=["scorer", "enemy_team_character"]
    ),
    SceneTemplate(
        text="<b>{scorer}</b> б'є з гострого кута, <b>{enemy_team_character}</b> не очікував такого рішення! М'яч у сітці! Хитрий гол! 😏",
        required_positions=["scorer", "enemy_team_character"]
    ),
    SceneTemplate(
        text="<b>{scorer}</b> потужно пробиває по центру воріт, <b>{enemy_team_character}</b> не встигає зреагувати на силу удару! Прошив воротаря! 🚀",
        required_positions=["scorer", "enemy_team_character"]
    ),
]


class TemplatesMatch(Enum):
    # Текст адаптирован под более быстрый и напряженный формат блиц-турнира 2v2
    START_MATCH = """
⚔️ Розпочинається напружений бліц-матч 2 на 2 між командами <b>{name_first_team}</b> та <b>{name_second_team}</b>!

🏟️ Арена: Бліц-турнір

🔹 Бойові двійки готові до бою:
- <b>{name_first_team}</b>: загальна сила <b>{power_first_team:.2f}</b> 
- <b>{name_second_team}</b>: загальна сила <b>{power_second_team:.2f}</b>

🔥 Хто вийде переможцем у цій швидкій сутичці? Поїхали! 🏆
"""

    TEMPLATE_PARTICIPANTS_MATCH = """
📋 <b>Склади команд на бліц-матч:</b>

🔸 <b>{name_first_team}</b>
- Гравці: 
{players_first_club}

🔸 <b>{name_second_team}</b>
- Гравці: 
{players_second_club}

🏆 Гра обіцяє бути швидкою та видовищною!
"""

    TEMPLATE_PARTICIPANT = """
👤 {character_name} | ⚔️ Сила: <b>{power_user:.2f}</b> | 📈 Рівень: <b>{lvl}</b>"""

    TEMPLATE_COMING_GOAL = """  
⚽️ <b>Вирішальний момент епізоду вже близько!</b> ⚽️  

🔥 <b>Поточні шанси на гол:</b>  
- ⚽️ Команда {name_first_team}: <b>{chance_first_team:.2f}%</b>  
- ⚽️ Команда {name_second_team}: <b>{chance_second_team:.2f}%</b>  

💥 <b>Це момент істини!</b>
Ваша енергія може стати тим самим поштовхом, що змінить усе — підтримайте свою команду! 🚀

✨ <b>Досягніть {min_donate_energy_bonus} енергії</b> в цьому епізоді — і отримаєте буст <b>+{koef_donate_energy}% до суми донату</b>!
Цей бонус посилить удар і збільшить шанси забити гол! ⚡️

⏳ У вас лише <b>30 секунд</b>, щоб вплинути на результат!
<b>Надішліть енергію</b> — і допоможіть своїй команді перемогти! 🥅🏆
"""

    TEMPLATE_END = """
🎉 Бліц-матч між командами <b>{name_first_team}</b> та <b>{name_second_team}</b> завершено! 

📊 Кінцевий рахунок: <b>{goals_first_team}</b> - <b>{goals_second_team}</b>.

{match_information}

🏆 Дякуємо командам за видовищну гру та справжній дух суперництва!
    """
    TEMPLATE_END_CONSIDER_POWER = """
    🎉 Бліц-матч між командами <b>{name_first_team}</b> та <b>{name_second_team}</b> завершено! 

    📊 Кінцевий рахунок: <b>{goals_first_team}</b> - <b>{goals_second_team}</b>.

    {match_information}

    🏆 Дякуємо командам за видовищну гру та справжній дух суперництва!
        """

    DRAW_TEMPLATE = """
Матч завершився внічию! Обидві команди билися гідно! 🤝
"""

    WIN_LOSE_TEMPLATE = """
Переможець: <b>{winner_team_name}</b>! 
Програла: <b>{loser_team_name}</b>.
"""

    TEMPLATE_REWARD_CHARACTER = """
🎁 Нагорода за твій виступ у бліц-матчі:

🏅 Ти показав чудову гру, і ось твої нагороди:

- 🎖 EXP: +{exp}
- 🪙 Money: +{money}
"""

    TEMPLATE_NO_CHARACTERS_IN_MATCH = """
⚠️ <b>На жаль, на цей бліц-матч не з'явились гравці!</b>

❌ Гра не відбулася.

🔜 <b>Не засмучуйся!</b> Тренуйся та готуйся до наступних битв. Твої перемоги ще попереду!

⚽️ Залишайся з нами, нові матчі вже скоро!
"""

    TEMPLATE_SCORE = """
⚽️ <b>{scoring_team}</b> забиває гол!

🏟 Матч: <b>{name_first_team}</b> — <b>{name_second_team}</b>
📊 Рахунок: <b>{goals_first_team}</b> - <b>{goals_second_team}</b>
"""

    TEMPLATE_MVP_CONGRATULATION = """
🔥 У цьому бліці яскраво проявили себе два гравці — вони стають <b>MVP зустрічі</b>!

Їхній внесок у гру був вирішальним, і за це вони отримують заслужені нагороди. 👏

🎁 <b>Нагороди вже нараховано кожному з MVP:</b>
- 🔑Ключ на тренування з тренером
{text_mvp_characters}
Велика повага цим лідерам!
"""
    TEMPLATE_MVP_PLAYER_POINTS = """
⭐️ <b>{nickname}</b> — {points} очок
"""


class GetterTemplatesMatch:

    def __init__(self, match_data: BlitzMatchData) -> None:
        self.match_data = match_data

    def format_message(
            self,
            template: TemplatesMatch,
            extra_context: dict = {}
    ) -> str:
        context = {
            'name_first_team': self.match_data.first_team.team_name,
            'name_second_team': self.match_data.second_team.team_name,
            'goals_first_team': self.match_data.first_team.goals,
            'goals_second_team': self.match_data.second_team.goals,
            'power_first_team': self.match_data.first_team.team_power,
            'power_second_team': self.match_data.second_team.team_power,
            'members_first_team': len(self.match_data.first_team.characters_in_match),
            'members_second_team': len(self.match_data.second_team.characters_in_match)
        }
        if extra_context:
            context.update(extra_context)
        return template.value.format(**context)