import random
from asyncio import Semaphore
from datetime import datetime, timedelta

from database.models.blitz_team import BlitzTeam
from database.models.character import Character
from .goal_generator import GoalGenerator
from ..constans import TIME_EVENT_DONATE_ENERGY, TIME_BLITZ_FIGHT
from ..entities import BlitzMatchData, MatchTeamBlitz
from ..enum_blitz_match import TypeGoalEvent
from ..message_sender.match_sender import BlitzMatchSender
from ...services.blitz_character_service import BlitzCharacterService

semaphore_add_key = Semaphore(2)


class BlitzMatch:
    SCORE_POINTS_BY_EVENT = {
        TypeGoalEvent.GOAL: 1,
        TypeGoalEvent.NO_GOAL: 0.25
    }

    def __init__(
            self,
            match_data: BlitzMatchData,
            start_time: datetime
    ) -> None:

        self.match_data = match_data
        self.match_sender = BlitzMatchSender(match_data)
        self.count_goals = self._generate_count_goals()

        end_time = start_time + TIME_BLITZ_FIGHT

        self.goal_generator = GoalGenerator(
            start_time=start_time,
            end_time=end_time,
            count_goals=self.count_goals
        )

    def _generate_count_goals(self) -> int:
        choices = [1] * 5 + [3] * 60 + [5] * 35
        count = random.choice(choices)
        return count

    async def start_match(self) -> tuple[BlitzTeam, BlitzTeam]:
        await self.match_data.init_teams()

        await self.goal_generator.start()
        await self.match_sender.start_match()
        await self.match_sender.send_participants_match()
        await self.event_watcher()
        winner_team, looser_team = await self.end_match()
        return winner_team.team, looser_team.team

    async def event_watcher(self) -> None:
        event_func: dict[TypeGoalEvent, callable] = {
            TypeGoalEvent.NO_GOAL: self.no_goal_event,
            TypeGoalEvent.PING_DONATE_ENERGY: self.ping_donate_energy_event,
            TypeGoalEvent.GOAL: self.goal_event,
        }

        async for event in self.goal_generator.generate_goals():
            if event is None:
                break
            await event_func[event]()
            for team in self.match_data.all_teams:
                team.anulate_donate_energy()

    async def no_goal_event(self) -> None:
        TYPE_EVENT = TypeGoalEvent.NO_GOAL

        first_character = self.match_data.first_team.get_character_by_power()
        second_character = self.match_data.second_team.get_character_by_power()
        characters_scene = [character for character in [first_character, second_character] if character]
        await self.match_sender.send_event_scene(
            goal_event=TYPE_EVENT,
            characters_scene=characters_scene
        )
        for character in [first_character, second_character]:
            if not character:
                continue

            await self._add_event(
                character=character,
                score_add=0.25
            )

    async def ping_donate_energy_event(self) -> None:
        goal_time = (
                datetime.now() + timedelta(seconds=TIME_EVENT_DONATE_ENERGY)
        ).timestamp()
        await self.match_sender.send_ping_donate_energy(int(goal_time))

    async def goal_event(self) -> None:
        goal_team = self.match_data.get_goal_team()
        goal_team.add_goal()
        character_goal = goal_team.get_character_by_power()
        if not character_goal:
            return

        assist_character = goal_team.get_character_by_power(
            no_character=character_goal
        )
        character_enemy = self.match_data.get_opposite_team(
            goal_team.team_id).get_character_by_power() if random.random() > 0.5 else None
        await self.match_sender.send_event_scene(
            goal_event=TypeGoalEvent.GOAL,
            character_goal=character_goal,
            goal_team=goal_team,
            character_assist=assist_character,
            character_enemy=character_enemy
        )
        await self._add_event(
            character=character_goal,
            score_add=1
        )
        await BlitzCharacterService.add_goal_to_character(
            character_id=character_goal.id,
        )

        if assist_character:
            await self._add_event(
                character=assist_character,
                score_add=0.75
            )

    async def end_match(self) -> tuple[MatchTeamBlitz, MatchTeamBlitz]:
        winner_match_team, required_consider_power = await self.match_data.get_winner_team()
        await self.match_sender.send_end_match(winner_match_team, required_consider_power)
        lose_team = self.match_data.get_opposite_team(winner_match_team.team_id)
        return winner_match_team, lose_team

    async def _add_event(
            self,
            character: Character,
            score_add: float = 0.25
    ) -> None:
        await BlitzCharacterService.add_score_to_character(
            character_id=character.id,
            add_score=score_add
        )
