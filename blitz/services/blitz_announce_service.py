import asyncio

from blitz.blitz_match.constans import END_BLITZ_PHOTO, BLITZ_STAGES_PATCH
from blitz.services.blitz_team_service import BlitzTeamService
from blitz.services.message_sender.blitz_sender import send_message_all_characters
from database.models.blitz_team import BlitzTeam
from database.models.character import Character


class BlitzAnnounceService:
    PARSE_MODE = 'HTML'

    @classmethod
    async def announce_matchups(cls, characters: list[Character], pairs: list[tuple[BlitzTeam, BlitzTeam]]):
        if not pairs:
            raise ValueError("На жаль, пар для матчів не знайдено.")

        stage_map = {
            16: ("1/16 фіналу", BLITZ_STAGES_PATCH[0]),
            8: ("1/8 фіналу", BLITZ_STAGES_PATCH[0]),
            4: ("1/4 фіналу", BLITZ_STAGES_PATCH[1]),
            2: ("1/2 фіналу", BLITZ_STAGES_PATCH[2]),
            1: ("Фінал", BLITZ_STAGES_PATCH[3]),
        }
        stage = stage_map.get(len(pairs), ("Наступний раунд", BLITZ_STAGES_PATCH[0]))

        lines = [f"⚽️ <b>Анонс бліц-раунду ({stage[0]})!</b> ⚽️", ""]
        for idx, (team_a, team_b) in enumerate(pairs, start=1):
            lines.append(f"🔸 Матч {idx}: <b>{team_a.name}</b> vs <b>{team_b.name}</b>")
        lines.append("")
        lines.append("⏳ У вас 60 секунд. Підготуйтеся до старту!")
        lines.append("Нехай переможе найсильніший! 💥")

        text = "\n".join(lines)
        await send_message_all_characters(characters, text, photo_path=stage[1])

    @classmethod
    async def announce_end(cls, characters: list[Character], final_winner: BlitzTeam, final_looser: BlitzTeam) -> None:
        res_winner, res_looser = await asyncio.gather(
            BlitzTeamService.get_characters_from_blitz_team(final_winner),
            BlitzTeamService.get_characters_from_blitz_team(final_looser)
        )
        ch_win_first = res_winner[0].owner.user_name if res_winner[0].owner.user_name else res_winner[0].character_name
        ch_win_second = res_winner[1].owner.user_name if res_winner[1].owner.user_name else res_winner[1].character_name
        ch_loose_first = res_looser[0].owner.user_name if res_looser[0].owner.user_name else res_looser[0].character_name
        ch_loose_second = res_looser[1].owner.user_name if res_looser[0].owner.user_name else res_looser[0].character_name
        end_text = f"""
🏆 <b>Результати блиц-турніру!</b>

🥇 Команда <b>«{final_winner.name}»</b> здобуває 1 місце та отримує середній лутбокс! Вітаємо {ch_win_first} і {ch_win_second} — справжні чемпіони! 🎉

🥈 Команда <b>«{final_looser.name}»</b> посідає 2 місце та отримує маленький лутбокс — чудова гра від {ch_loose_first} і {ch_loose_second}! 👏

⚡ Усі учасники отримують +30 енергії! Дякуємо за гру — до наступного блиц-турніру! 💪
"""
        await send_message_all_characters(characters, end_text, photo_path=END_BLITZ_PHOTO)

    @classmethod
    async def announce_round_results(cls,
                                     characters: list[Character],
                                     winners: list[BlitzTeam],
                                     losers: list[BlitzTeam]):
        if not winners and not losers:
            raise ValueError("Немає даних про результати раунду.")

        next_stage_map = {
            16: "1/8 фіналу",
            8: "1/4 фіналу",
            4: "1/2 фіналу",
            2: "ФІНАЛ 🏆",
            1: "Матч за 3-є місце"
        }
        next_stage = next_stage_map.get(len(winners), "Наступний раунд")

        lines = [f"🔔 <b>Результати раунду!</b> 🔔", ""]
        if losers:
            lines.append("🚫 <b>Вибули:</b>")
            for team in losers:
                lines.append(f"- {team.name}")
            lines.append("")
        if winners:
            lines.append("✅ <b>Пройшли далі:</b>")
            for team in winners:
                lines.append(f"- {team.name}")
            lines.append("")
        lines.append(f"🔥 <b>Наступний етап: {next_stage}!</b> 🔥")

        # Нотифікація команд індивідуально
        for w in winners:
            await cls.notify_team_advancement(w, next_stage)
        for l in losers:
            await cls.notify_team_elimination(l)

        text = "\n".join(lines)
        await send_message_all_characters(characters, text)

    @classmethod
    async def notify_team_advancement(cls,
                                      team: BlitzTeam,
                                      next_stage: str):
        char_a, char_b = await BlitzTeamService.get_characters_from_blitz_team(team)
        prep_text = 'раунду який вирішить долю вашої команди у цьому Бліц турнірі 🔥' if next_stage == 'ФІНАЛ 🏆' else 'наступного раунду'
        text = (
            f"🎉 Ваша команда <b>{team.name}</b> проходить у <b>{next_stage}</b>! 🎉\n"
            f"У вас є 60 секунд на підготовку до {prep_text}. ⏱️"
        )
        await send_message_all_characters([char_a, char_b], text)

    @classmethod
    async def notify_team_elimination(cls,
                                      team: BlitzTeam):
        char_a, char_b = await BlitzTeamService.get_characters_from_blitz_team(team)
        text = (
            f"⚠️ Ваша команда <b>{team.name}</b> не пройшла далі цього раунду. ⚠️\n"
            f"Дякуємо за участь! Наприкінці турніру вам буде нараховано +50 енергії."
        )
        await send_message_all_characters([char_a, char_b], text)
