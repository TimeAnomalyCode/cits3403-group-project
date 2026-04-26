import math
import secrets
import sqlalchemy as sa

from game2048.models import MatchPlayer, Match, Tournament, User
from game2048 import db

def create_tournament(current_user_id):
    tournament_code = secrets.token_hex(3)

    while True:
        tournament_code = secrets.token_hex(3)  # generate a random 6-character code (3 bytes hex)
        
        # query the database: check if this code already exists
        exists = db.session.scalar(
            sa.select(Tournament).where(Tournament.tournament_code == tournament_code)
        )
        # if it doesn't exist, break the loop and use this code
        if not exists:
            break

    tournament = Tournament(
        tournament_code=tournament_code,  
        host_user_id=current_user_id,
        status='pending'
    )

    db.session.add(tournament)
    db.session.flush()  

    # initialize 2 matches 
    initial_matches = [
        Match(tournament_id=tournament.id, round_number=1, match_number=1, ),
        Match(tournament_id=tournament.id, round_number=1, match_number=2),
    ]
    db.session.add_all(initial_matches)
    db.session.flush()  # 让 Match 获得 id

    first_match = initial_matches[0]

    # register the host player to the first match by default
    """ This is part no complete"""
    mp = MatchPlayer(
        match_id=first_match.id,
        user_id=current_user_id
    )
    db.session.add(mp)
    db.session.commit()

    return  tournament_code  # return tournament.id


def get_simple_bracket(tournament_code):
    """
    Get tournment player names for the first round, and generate a simple bracket structure for the frontend to render.
    return format：
    [
        [ ["Alice", "Bob"], ["Charlie", "Waiting"] ],  # Round 1
        [ ["", ""], ["", ""] ],  # Round 2 (占位)
        [ ["", ""], ["", ""] ],  # Round 3 (占位)
        ...
    """
    # 1. find tournament by code
    tournament = db.session.scalar(
        db.select(Tournament).where(Tournament.tournament_code == tournament_code)
    )
    if not tournament:
        return []

    # 2. get all match in these tournament where round_number = 1 (first round)
    round1_matches = db.session.scalars(
        db.select(Match)
        .where(Match.tournament_id == tournament.id)
        .where(Match.round_number == 1)
        .order_by(Match.match_number)
    ).all()

    # 3. get player names for these matches 
    player_names = []
    for match in round1_matches:
        # 取出这场比赛的两个玩家
        players_in_match = db.session.scalars(
            db.select(User)
            .join(MatchPlayer, User.id == MatchPlayer.user_id)
            .where(MatchPlayer.match_id == match.id)
        ).all()

        if len(players_in_match) >= 1:
            player_names.append(players_in_match[0].username)
        else:
            player_names.append("Waiting")

        if len(players_in_match) >= 2:
            player_names.append(players_in_match[1].username)
        else:
            player_names.append("Waiting")

    num_players = len(player_names)
    if num_players < 2:
        num_players = 4  
        player_names = ["Waiting", "Waiting", "Waiting", "Waiting"]

    # 5. gen bracket for the first round (pairing every 2 players)
    first_round = []
    for i in range(0, num_players, 2):
        p1 = player_names[i] if i < len(player_names) else "Waiting"
        p2 = player_names[i+1] if i+1 < len(player_names) else "Waiting"
        first_round.append([p1, p2])

    all_rounds = [first_round]
    # total_rounds = int(math.log2(num_players))

    # empty matches for future rounds 
    current_matches = len(first_round) // 2
    while current_matches >= 1:
        all_rounds.append([["", ""] for _ in range(current_matches)])
        current_matches = current_matches // 2

    return all_rounds

# These functions are for the "Add More Matches" button, 
# which allows the host to expand the tournament bracket 
def add_more_matches(tournament):

    # Calculate how many matches to add 
    match_count = math.log(len(tournament.matches), 2)   
    match_count = int(2 ** (match_count + 1) - len(tournament.matches) )# Only allow 2, 4, 8, 16 matches (1, 2, 3, 4 rounds) to keep the bracket clean

    # Generate new matches with correct match_number
    new_matches = []
    for i in range(match_count):
        # To calculate the next match_number
        last_match = db.session.scalar(
            sa.select(Match)
            .where(Match.tournament_id == tournament.id)
            .order_by(Match.match_number.desc())
        )
        next_match_num = last_match.match_number + 1 if last_match else 1

        new_match = Match(
            tournament_id=tournament.id,
            round_number=1,
            match_number=next_match_num
        )
        new_matches.append(new_match)

    db.session.add_all(new_matches)
    db.session.commit()
