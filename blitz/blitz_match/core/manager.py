from blitz.blitz_match.entities import BlitzMatchData


class TeamBlitzMatchManager:
    all_matches: dict[str, BlitzMatchData] = {}

    @classmethod
    def add_match(cls, match_data: BlitzMatchData) -> None:
        cls.all_matches[match_data.blitz_match_id] = match_data

    @classmethod
    def get_match(cls, blitz_match_id: str) -> BlitzMatchData | None:
        return cls.all_matches.get(blitz_match_id, None)

    @classmethod
    def clear_matches(cls) -> None:
        cls.all_matches.clear()
