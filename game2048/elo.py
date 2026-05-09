from sqlalchemy import or_
from game2048.models import Match


def expected(player1Elo, player2Elo):
    return 1 / (1 + pow(10, (player1Elo - player2Elo) / 400))


def getMatchCount(userID: int):
    return Match.query.filter(
        or_(Match.player1_id == userID, Match.player2_id == userID)
    ).count()


def getK(matchCount: int):
    if matchCount < 15:
        return 40
    elif matchCount < 30:
        return 20
    else:
        return 10


def update_elo(winner, loser):
    WinnerMatchCount = getMatchCount(winner.id)
    loserMatchCount = getMatchCount(loser.id)
    winnerK = getK(WinnerMatchCount)
    loserK = getK(loserMatchCount)
    winnerExpected = expected(winner.elo, loser.elo)
    loserExpected = expected(loser.elo, winner.elo)
    newWinnerElo = round(winner.elo + winnerK * (1 - winnerExpected))
    newLoserElo = round(loser.elo + loserK * (0 - loserExpected))
    return newWinnerElo, newLoserElo
