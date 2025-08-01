

async def test():
    
    first_club = MatchClub(
        club_id = 83
    )
    second_club = MatchClub(
        club_id = 228
    )
    start_data = datetime.now() 
    match_data = MatchData(
        match_id = "123",
        group_id = "123",
        first_club = first_club,
        second_club = second_club,
        start_time = start_data,
    )
    match = Match(
        match_data = match_data,
        start_time = start_data,
    )
    ClubMatchManager.add_match(match_data)
    await match.start_match()