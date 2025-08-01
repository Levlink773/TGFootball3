from typing import Tuple

from match.entities import MatchData

class ClubMatchManager:
    all_matches: dict[str, MatchData] = {}

    @classmethod
    def add_match(cls, match_data: MatchData) -> None:
        cls.all_matches[match_data.match_id] = match_data
        
    @classmethod
    def get_match(cls, match_id: str) -> MatchData | None:
        return cls.all_matches.get(match_id, None)
    
    @classmethod
    def get_matches_by_club(cls, club_id: str) -> Tuple[MatchData, MatchData]:
        """Get all matches for a specific club."""
        return [
            match for match in cls.all_matches.values() 
                if match.first_club_id == club_id 
                    or 
                match.second_club_id == club_id
            ]