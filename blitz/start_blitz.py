import asyncio
import random
from datetime import datetime, time, timedelta

from blitz.blitz_match.core.manager import TeamBlitzMatchManager
from blitz.blitz_match.core.match import BlitzMatch
from blitz.blitz_match.entities import MatchTeamBlitz, BlitzMatchData
from blitz.blitz_match.utils import generate_blitz_match_id
from blitz.blitz_reminder import BlitzReminder
from blitz.enum_blitz import BlitzStatus
from blitz.services.blitz_announce_service import BlitzAnnounceService
from blitz.services.blitz_reward_service import BlitzRewardService, RewardWinnerBlitzTeam, RewardPreWinnerBlitzTeam, \
    RewardSimpleBlitzTeam
from blitz.services.blitz_service import BlitzService
from blitz.services.blitz_team_service import BlitzTeamService
from blitz.services.message_sender.blitz_sender import BlitzTeamSender
from database.models.blitz import Blitz
from database.models.blitz_team import BlitzTeam
from database.models.character import Character
from logging_config import logger


class StartBlitzs:
    @staticmethod
    async def start(start_times: list[time]):
        StartBlitzs.validate_start_times(start_times)

        while True:
            now = datetime.now()
            next_start_datetime = None

            for t in sorted(start_times):
                potential_start = datetime.combine(now.date(), t)
                if potential_start < now:
                    potential_start += timedelta(days=1)

                if next_start_datetime is None or potential_start < next_start_datetime:
                    next_start_datetime = potential_start
            logger.info(f"Планирую следующий блиц на {next_start_datetime}")
            await StartBlitz(next_start_datetime).start()
            await asyncio.sleep(1)

    @staticmethod
    def validate_start_times(start_times: list[time]):
        minutes = [
            t.hour * 60 + t.minute
            for t in sorted(start_times)
        ]
        for i in range(1, len(minutes)):
            delta = minutes[i] - minutes[i - 1]
            if delta < 60:
                raise ValueError(
                    f"Времена {start_times[i - 1]} и {start_times[i]} находятся ближе чем за 1 час"
                )
        if len(minutes) >= 2:
            wrap_around_delta = (1440 - minutes[-1]) + minutes[0]
            if wrap_around_delta < 60:
                raise ValueError(
                    f"Времена {start_times[-1]} и {start_times[0]} (через полночь) находятся ближе чем за 1 час"
                )


class StartBlitz:
    def __init__(self, start_datetime: datetime, stages_of_final: int = 5):
        self.start_datetime = start_datetime.replace(microsecond=0)
        if stages_of_final <= 1:
            raise ValueError("count of final must be greater than 1")
        self.stages_of_final = stages_of_final
        self.necessary_users = 2 ** stages_of_final

    @staticmethod
    async def _start_blitz_match(teams: tuple[BlitzTeam, BlitzTeam], stage: int) -> tuple[BlitzTeam, BlitzTeam]:
        first_team_id = teams[0].id
        second_team_id = teams[1].id
        logger.info(f"teams for match: {teams}")
        match_team_first = MatchTeamBlitz(team_id=first_team_id)
        match_team_second = MatchTeamBlitz(team_id=second_team_id)
        blitz_match_id = generate_blitz_match_id(first_team_id, second_team_id)
        logger.info(f"blitz_match_id: {blitz_match_id}, stage: {stage}")
        match_data = BlitzMatchData(
            blitz_match_id=blitz_match_id,
            stage=stage,
            first_team=match_team_first,
            second_team=match_team_second
        )
        TeamBlitzMatchManager.add_match(match_data)
        blitz_match = BlitzMatch(match_data, datetime.now())
        winner_team, looser_team = await blitz_match.start_match()
        return winner_team, looser_team

    async def _start_blitz(self, blitz_id: int):
        teams: list[BlitzTeam] = await BlitzTeamService.create_teams(
            team_count=int(self.necessary_users / 2),
            blitz_id=blitz_id
        )
        logger.info("Teams created")
        random.shuffle(teams)
        await BlitzTeamSender.send_teams_message(teams)
        logger.info("Teams sended")
        characters: list[Character] = await BlitzService.get_characters_from_blitz_character(blitz_id)
        looser_team = []
        while len(teams) > 2:

            pair_teams = BlitzTeamService.pair_teams(teams)
            logger.info(f"pair_teams: {pair_teams} for stage {len(pair_teams)}")
            asyncio.create_task(BlitzAnnounceService.announce_matchups(characters, pair_teams))
            await asyncio.sleep(60)
            tasks = [
                StartBlitz._start_blitz_match((first, second), len(pair_teams))
                for first, second in pair_teams
            ]
            logger.info(f"tasks: {tasks}")
            logger.info("blitz match started")
            results_match = await asyncio.gather(*tasks)
            logger.info(f"blitz match finish: {results_match}")
            looser_teams_stage = [looser for _, looser in results_match]
            winner_teams_stage = [winner for winner, _ in results_match]
            logger.info(f"winner_teams_stage: {winner_teams_stage}")
            logger.info(f"looser_teams_stage: {looser_team}")
            asyncio.create_task(BlitzAnnounceService.announce_round_results(characters, winner_teams_stage, looser_teams_stage))
            looser_team.extend(looser_teams_stage)
            teams = winner_teams_stage
        pair_teams = [(teams[0], teams[1])]
        logger.info(f"pair_teams final: {pair_teams}")
        asyncio.create_task(BlitzAnnounceService.announce_matchups(characters, pair_teams))
        await asyncio.sleep(60)
        logger.info("Blitz match final started")
        final_winner, final_looser = await StartBlitz._start_blitz_match(pair_teams[0], 1)
        logger.info(f"final_winner: {final_winner}")
        bz_reward = BlitzRewardService.reward_blitz_team
        await asyncio.gather(
            bz_reward(RewardWinnerBlitzTeam(final_winner)),
            bz_reward(RewardPreWinnerBlitzTeam(final_winner)),
            *[
                bz_reward(RewardSimpleBlitzTeam(lose_team))
                for lose_team in looser_team
            ]
        )
        logger.info("Reward blitz match")
        asyncio.create_task(BlitzAnnounceService.announce_end(characters, final_winner, final_looser))
        TeamBlitzMatchManager.clear_matches()
        return final_winner

    async def start(self) -> BlitzStatus:
        blitz: Blitz = await BlitzService().get_or_create_blitz_by_start(self.start_datetime)

        status = await BlitzReminder(blitz, necessary_count_users=self.necessary_users).remind()
        if not status:
            logger.warn("Блиц турнир отменен!")
            return BlitzStatus.CANCELED
        logger.info("🏁 Блиц начинается!")
        await self._start_blitz(blitz.id)
        logger.info("🏁 Блиц завершен!")
        await BlitzService.remove_blitz_by_id(blitz.id)
        logger.info("🏁 Блиц удален!")
        return BlitzStatus.FINISH
