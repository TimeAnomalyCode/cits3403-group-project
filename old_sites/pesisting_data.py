
# persist data
class TourementData:
    
    def __init__(self):
        self.players = []
        self.match_id = []
        self.match = {} #match_id : [player1, player2]
        

    def add_match(self,match_id, p1,p2):
        self.match[match_id] = [p1,p2]
    
    def remove_match(self, match_id):
        self.match.pop(match_id)

    def add_player(self,username):
        self.players.append(username)
    
    def remove_player(self, username):
        self.players.remove(username)


