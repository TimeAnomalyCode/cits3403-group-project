from flask import Flask, request ,render_template
from flask_socketio import SocketIO, join_room
import uuid
import time
GAMETIME = 10
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
# Note: cors_allowed_origins="*" is for dev, should change to specific port

class PlayerState:
    # a user game data that should be received by the backend
    def __init__(self):
        self.cells  = [[0,0,0,0],
                      [0,0,0,0],
                      [0,0,0,0],
                      [0,0,0,0]]
        self.score = 0
        self.won = False
        self.dead = False
        self.hiddenScore = 0 
        self.trashPoint = 0
        self.matchID = None
        pass

class moveTile:
    # remove 0 and move all to left
    @staticmethod
    def compress(row):
        new = []
        for i in row:
            if i != 0:
                new.append(i)
        return new

    # compare and merge
    @staticmethod
    def merge(row):
        score = 0
        for i in range(len(row)-1):
            if row[i] == row[i+1]:
                row[i] = row[i] * 2
                row[i+1] = 0

                score += row[i]
            elif row[i] < 0 or row[i+1] < 0:
                s = row[i] + row[i+1]
                if s == 0:
                    row[i] = 0
                    row[i+1] = 0
        return row, score
    
    @staticmethod
    def left(cell):
        new_cell = []
        Total_score_for_move = 0
        moved = False

        for r in cell:
            row = moveTile.compress(r)
            row, score = moveTile.merge(row)
            row = moveTile.compress(row)
            
            length = len(r) - len(row)
            
            # fill back with 0
            for i in range(length):
                row.append(0)

            if row != r:
                moved = True
            
            new_cell.append(row)
            Total_score_for_move += score
        
        return new_cell, moved, Total_score_for_move
    
    @staticmethod     
    def right(cell):
        reverse_cell = []
        temp_cell = []
        for i in cell:
            reverse_cell.append(i[::-1])
        new_cell, moved, Total_score_for_move = moveTile.left(reverse_cell)
        for r in new_cell:
            temp_cell.append(r[::-1])
        new_cell = temp_cell
        return new_cell, moved, Total_score_for_move

    @staticmethod
    def transform(cell): 
        new_cell = []

        # transform
        for c in range(len(cell)):
            new_array = []
            for r in cell:
                new_array.append(r[c])
            #print(new_array)
            new_cell.append(new_array)
        return new_cell   


    @staticmethod     
    def up(cell):
        # new_cell = []
        Total_score_for_move = 0
        moved = False

        # for i in range(len(cell)):
        #     new_cell.append([])

        # transform
        # for c in range(len(cell)):
        #     new_array = []
        #     for r in cell:
        #         new_array.append(r[c])
        #     print(new_array)
        #         #end of transform
        #     column = moveTile.compress(new_array)
        #     column, score = moveTile.merge(column)
        #     column = moveTile.compress(column)

        #     length = len(new_array) - len(column)

        #     for i in range(length):
        #         column.append(0)

        #     if new_array != column:
        #         moved = True
            
        #     for l in range(len(column)):
        #         new_cell[l].append(column[l])
            
        #     Total_score_for_move += score

        cell = moveTile.transform(cell)
        # print(cell)
        cell2 = []
        for c in cell:
            column = moveTile.compress(c)
            column, score = moveTile.merge(column)
            column = moveTile.compress(column)

            length = len(c) - len(column)

            for i in range(length):
                column.append(0)

            if c != column:
                moved = True
            #print(column)
            cell2.append(column)
            # for l in range(len(column)):
            #     new_cell[l].append(column[l])
        
            Total_score_for_move += score
        # print(cell2)
        new_cell = moveTile.transform(cell2)
        # print(cell2)
        return new_cell, moved, Total_score_for_move
    
    @staticmethod  
    def down(cell):
        Total_score_for_move = 0
        moved = False
        cell = moveTile.transform(cell)
        print(cell)
        cell2 = []
        for c in cell:
            c = c[::-1]
            column = moveTile.compress(c)
            column, score = moveTile.merge(column)
            column = moveTile.compress(column)

            length = len(c) - len(column)

            for i in range(length):
                column.append(0)

            if c != column:
                moved = True
            #print(column)
            column = column[::-1]
            cell2.append(column)
            Total_score_for_move += score
        # print(cell2)
        new_cell = moveTile.transform(cell2)
        # print(cell2)
        return new_cell, moved, Total_score_for_move
    
    @staticmethod
    def hasMove(cell):
        N = len(cell)
        for r in range(N):
            for c in range(N):
                if cell[r][c] == 0:
                    return True
                if c < N - 1 and cell[r][c] == cell[r][c+1]:
                    return True
                if r < N - 1 and cell[r][c] == cell[r+1][c]:
                    return True
                if c < N - 1 and (cell[r][c] + cell[r][c+1]) <= 0:
                    return True
                if r < N - 1 and (cell[r][c] + cell[r+1][c]) <= 0:
                    return True
        return False

# seeded pseudo-random number generators
# Source - https://stackoverflow.com/a/424445
#import random
# fixed the overflow inconsistance between js and python
class Seededrandom:
    def __init__(self, seed=None):
        self.m = 2**31
        self.a = 1103515245
        self.c = 12345

        if seed is None:
            import random
            seed = random.randint(0, self.m - 1)

        self.state = seed
        self.state = (self.a * self.state + self.c) & 0x7fffffff

    def next_int(self):
        self.state = (self.a * self.state + self.c) & 0x7fffffff
        return self.state

    def next_float(self):
        return self.next_int() / (self.m - 1)

    def next_range(self, start, end):
        range_size = end - start
        random_under_1 = self.next_int() / self.m
        return start + int(random_under_1 * range_size)

    def choice(self, array):
        return array[self.next_range(0, len(array))]

# global seed
Seed = Seededrandom(seed=4)
class randomness:
    @staticmethod
    def randomPickEmpty(cell):
        N = len(cell)
        empty_space = []

        for r in range(N):
            for c in range(N):
                if cell[r][c] == 0:
                    empty_space.append([r,c])

        if len(empty_space) == 0:
            return None, None
        
        #pick = random.randint(0,len(empty_space)-1)
        # Seed = Seededrandom(seed=4)
        pick = Seed.next_range(0,len(empty_space))

        [r,c] = empty_space[pick]
        
        print([r,c])
        return [r,c]
    @staticmethod
    def randomPickNonEmpty(cell):
        N = len(cell)
        empty_space = []

        for r in range(N):
            for c in range(N):
                if cell[r][c] > 0:
                    empty_space.append([r,c])

        if len(empty_space) == 0:
            return None, None
        
        # pick = random.randint(0,len(empty_space)-1)
        # Seed = Seededrandom(seed=4)
        pick = Seed.next_range(0,len(empty_space))


        [r,c] = empty_space[pick]
        
        print([r,c])
        return [r,c]
    
    @staticmethod
    def fisher_yates_shuffle(array):
        # Iterate from the last element down to the second element
        for i in range(len(array) - 1, 0, -1):
            # Pick a random index from 0 to i
            #j = random.randint(0, i)
            # Seed = Seededrandom(seed=4)
            j = Seed.next_range(0,i+1)
            # Swap elements at indices i and j
            array[i], array[j] = array[j], array[i]
        return array

class BoardState:
    
    @staticmethod
    def spawnTile(cell):
        # N = len(cell)
        # empty_space = []

        # for r in range(N):
        #     for c in range(N):
        #         if cell[r][c] == 0:
        #             empty_space.append([r,c])

        # if len(empty_space) == 0:
        #     return
        
        # pick = random.randint(0,len(empty_space)-1)

        # [r,c] = empty_space[pick]
        # print([r,c])
        r,c = randomness.randomPickEmpty(cell)
        
        if r == None or c == None:
            return cell
        
        #probability = random.random()
        # Seed = Seededrandom(seed=4)
        probability = Seed.next_float()
        if probability < 0.9:
            cell[r][c] = 2
        else:
            cell[r][c] = 4
        
        return cell
    def set_init(object):
        object.cells  = [[0,0,0,0],
                      [0,0,0,0],
                      [0,0,0,0],
                      [0,0,0,0]]
        object.score = 0
        object.won = False
        object.dead = False
        object.hiddenScore = 0 
        object.trashPoint = 0
        return
    

class GameFunction:

    @staticmethod
    def destroySpecificTile(cell): # destory random tile
        r,c = randomness.randomPickNonEmpty(cell)
        if r == None or c == None:
            return cell, False 
        
        cell[r][c] = 0
        return cell, True
        
    @staticmethod
    def createRandomTile(cell):
        r,c = randomness.randomPickEmpty(cell)
        if r == None or c == None:
            return cell, False 
        #cell[r][c] = 2 ** random.randint(1,6)
        # Seed = Seededrandom(seed=4)
        cell[r][c] = 2 ** Seed.next_range(1,7)
        return cell, True
    
    @staticmethod
    def rearrangeBoard(cell):
        N = len(cell)
        values = []

        for r in range(N):
            for c in range(N):
                if(cell[r][c] > 0):
                    values.append(cell[r][c])
                    cell[r][c] = 0
        
        values = randomness.fisher_yates_shuffle(values)

        empty = []
        for r in range(N):
            for c in range(N):
                if(cell[r][c] == 0):
                    empty.append([r,c])

        empty = randomness.fisher_yates_shuffle(empty)

        for i in range(len(values)):
            r,c = empty[i]
            cell[r][c] = values[i]
        
        return cell
    
    @staticmethod
    def makeRandomNegativeTile(cell):
        r,c = randomness.randomPickEmpty(cell)
        if r == None or c == None:
            return cell, False 
        #cell[r][c] = (-1) * 2 ** random.randint(1,3)
        # Seed = Seededrandom(seed=4)
        cell[r][c] = (-1) * 2 ** Seed.next_range(1,4)
        return cell, True

# == multi-player connection and communication part ==
players_dict = {}
waiting_player = None
room = {}
# == timer status== 
match_timers = {}
match_active = {}
match_started = {}
#add a timer and keep player on the same page
def countdown(players_dict, match):
    #set timer
    # match_timers[match] = 180

    while match_timers[match] > 0 and match_active.get(match, False):
        socketio.sleep(1)
        match_timers[match] -= 1
        print( match_timers[match], end="\r")  # Overwrites the same line
        
        
    print("Time's up!")
    #check
    return check_player_win_and_dead(players_dict, match)

def check_player_win_and_dead(players_dict, match):
    if not match_active.get(match,True):
        return
    
    # player = players_dict[request.sid]
    # match = player.matchID
    players = room[match]["players"]
    p1 = players_dict[players[0]]
    p2 = players_dict[players[1]]  
    print('check win dead',players[0],players[1])
    print("p1.score",p1.score)
    print("p2.score:",p2.score)

    #check
    if match_timers[match] == 0 or (p1.dead and p2.dead):
        if p1.score > p2.score:
            p1.won = True
            p2.dead = True
            print(f"winner is {players[0]}")
            # endgame
            name = players[0]
            socketio.emit("game_end", {"winner": name}, room=match)
            match_active[match] = False
            return players[0]
        elif p1.score < p2.score:
            p2.won = True
            p1.dead = True
            print(f"winner is {players[1]}")
            # endgame
            socketio.emit("game_end", {"winner": players[1]}, room=match)
            match_active[match] = False
            return players[1]
        else:
            print(f"winner is draw")
            restart_game(players_dict, match)
            return "draw"
    if p1.dead:
        socketio.emit("game_end", {"winner": players[1]}, room=match)
        match_active[match] = False
        return players[1]
        
    if p2.dead:
        socketio.emit("game_end", {"winner": players[0]}, room=match)
        match_active[match] = False
        return players[0]
def restart_game(players_dict, match):
    match_active[match] = False
    players = room[match]["players"]

    # send restart to frontend
    socketio.emit("game_restart", {"matchId": match}, room=match)
    
    for id in players:
        player = players_dict[id]

        BoardState.set_init(player)
        player.cells = BoardState.spawnTile(player.cells)
        player.cells = BoardState.spawnTile(player.cells)

        socketio.emit("update_init", {
            "cells": player.cells,
            "Pid": id,
            "MatchID": match
        }, to=id)

    match_timers[match] = GAMETIME
    match_active[match] = True

    socketio.start_background_task(countdown, players_dict, match)

@socketio.on('connect')
def handle_multiplayer_connect(auth=None):
    global waiting_player

    Pid = request.sid
    players_dict[Pid] = PlayerState()

    if waiting_player is None:
        waiting_player = Pid
        print(waiting_player)
    else:
        if waiting_player == Pid:
            return
        match = str(uuid.uuid4())
        join_room(match,sid=Pid)
        join_room(match,sid=waiting_player)

        players_dict[Pid].matchID = match
        players_dict[waiting_player].matchID = match
        
        # hello, stored player 
        room[match] = {
            "players": [waiting_player, Pid]
        }
        print(room[match])
        socketio.emit("start_game", {"room": match}, room=match)
        waiting_player = None     
timeing = 0
@socketio.on('disconnect')
def handle_multiplayer_disconnect():
    global waiting_player
    Pid = request.sid

    # remove player state
    players_dict.pop(Pid, None)

    # clean match making queue
    if waiting_player == Pid:
        waiting_player = None


@socketio.on("game_init")
def receive_init_communcation(data):
    player = players_dict[request.sid]
    
    print(data)
    print("Connected user is:",request.sid)
    if data == "start_game":
        # player1.cells = [[0,0,0,0],
        #               [0,0,0,0],
        #               [0,0,0,0],
        #               [0,0,0,0]]
        BoardState.set_init(player)
        player.cells = BoardState.spawnTile(player.cells)
        player.cells = BoardState.spawnTile(player.cells)
        pass
    # send back to own frontend
    socketio.emit("update_init", {
        "cells": player.cells,
        "Pid": request.sid,
        "MatchID":player.matchID
        },to=request.sid)
    
    #boardcast own board to second player
    match = player.matchID
    players = room[match]["players"]

    for i in players:
        if i != request.sid:
            socketio.emit("update_second_init", {
                "cells": player.cells,
                "Pid": request.sid,
                "MatchID":player.matchID
            }, to=i)
    

    if match_started.get(match,False):
        return 
    
    match_timers[match] = GAMETIME
    match_active[match] = True
    match_started[match] = True
    # starting a thread for timing, aviod blocking
    
    socketio.start_background_task(countdown, players_dict, match)


# player = PlayerState()
# def check_win_dead(player_dict, player_list):

# print(player.cells)
# == socket part ==
@socketio.on("game_direction")
def receive_direction_communcation(data):
    global timeing
    player = players_dict[request.sid]
    
    match = player.matchID
    #check match is still going and exit if not
    if not match_active.get(match, True):
        return
    
    print("Current user is:",request.sid)

    moved = False
    score = 0
    print("Before move:", player.cells)
    if data == "left":
        player.cells, moved, score = moveTile.left(player.cells)
        player.cells = BoardState.spawnTile(player.cells)
        player.score += score
        player.hiddenScore += score
        if player.hiddenScore > 128:
            player.trashPoint = player.trashPoint + 1
            player.hiddenScore = player.hiddenScore - 128
        if not moveTile.hasMove(player.cells):
            player.dead = True
        pass
    elif data == "right":
        player.cells, moved, score = moveTile.right(player.cells)
        player.cells = BoardState.spawnTile(player.cells)
        player.score += score
        player.hiddenScore += score
        if player.hiddenScore > 128:
            player.trashPoint = player.trashPoint + 1
            player.hiddenScore = player.hiddenScore - 128
        if not moveTile.hasMove(player.cells):
            player.dead = True
            
        
        socketio.emit("update", player.cells)
        pass
    elif data == "up":
        player.cells, moved, score = moveTile.up(player.cells)
        player.cells = BoardState.spawnTile(player.cells)
        player.score += score
        player.hiddenScore += score
        if player.hiddenScore > 128:
            player.trashPoint = player.trashPoint + 1
            player.hiddenScore = player.hiddenScore - 128
        if not moveTile.hasMove(player.cells):
            player.dead = True
        pass
    elif data == "down":
        player.cells, moved, score = moveTile.down(player.cells)
        player.cells = BoardState.spawnTile(player.cells)
        player.score += score
        player.hiddenScore += score
        if player.hiddenScore > 128:
            player.trashPoint = player.trashPoint + 1
            player.hiddenScore = player.hiddenScore - 128
        if not moveTile.hasMove(player.cells):
            player.dead = True
        pass
    # send back to frontend
    print(data)
    print("After move:", player.cells)

    #death determination logic, end game
    # check player state 
    # match = player.matchID
    if not match_active.get(match, True):
        return
    
    if player.dead or match_timers[match] == 0:
        check_player_win_and_dead(players_dict, match)

    socketio.emit("update_direction", {
        "cells": player.cells,
        "score": player.score,
        "won": player.won,
        "dead": player.dead,
        "hiddenScore": player.hiddenScore,
        "trashPoint": player.trashPoint
        }, room=request.sid)
    
    #boardcast own board to second player
    # match = player.matchID
    players = room[match]["players"]

    for i in players:
        if i != request.sid:
            socketio.emit("update_second_direction", {
                "cells": player.cells,
                "score": player.score,
                "won": player.won,
                "dead": player.dead,
                "hiddenScore": player.hiddenScore,
                "trashPoint": player.trashPoint
            }, to=i)


@socketio.on("game_function")
def receive_function_communcation(data):
    player = players_dict[request.sid]
    if data == "destroySpecificTile":
        # player1.cells, state = GameFunction.destroySpecificTile(player1.cells) #place for easy testing
        #the following has condition, harder in testing, so i seperate into two part of testing
        print("test")
        if player.trashPoint > 0:
            player.cells, state = GameFunction.destroySpecificTile(player.cells)
            print("hiddenScore", player.trashPoint, state)
            if state:
                player.trashPoint -= 1
        pass
    elif data == "createRandomTile":
        # player1.cells, state = GameFunction.createRandomTile(player1.cells) #place for easy testing
        #the following has condition, harder in testing, so i seperate into two part of testing
        if player.trashPoint > 0:
            player.cells, state = GameFunction.createRandomTile(player.cells)
            if state:
                player.trashPoint -= 1
        pass
    elif data == "rearrangeBoard":
        # player1.cells = GameFunction.rearrangeBoard(player1.cells) #place for easy testing
        #the following has condition, harder in testing, so i seperate into two part of testing
        if player.trashPoint > 0:
            player.cells = GameFunction.rearrangeBoard(player.cells)
            player.trashPoint -= 1
        pass
    elif data == "makeRandomNegativeTile":
        # player1.cells, state = GameFunction.makeRandomNegativeTile(player1.cells) #place for easy testing
        #the following has condition, harder in testing, so i seperate into two part of testing
        if player.trashPoint > 0:
            player.cells, state = GameFunction.makeRandomNegativeTile(player.cells)
            if state:
                player.trashPoint -= 1
        pass
    # send back to frontend
    socketio.emit("update_function", {
        "cells": player.cells,
        "score": player.score,
        "won": player.won,
        "dead": player.dead,
        "hiddenScore": player.hiddenScore,
        "trashPoint": player.trashPoint
        }, room=request.sid)
    
    #boardcast own board to second player
    match = player.matchID
    players = room[match]["players"]

    for i in players:
        if i != request.sid:
            socketio.emit("update_second_function", {
                "cells": player.cells,
                "score": player.score,
                "won": player.won,
                "dead": player.dead,
                "hiddenScore": player.hiddenScore,
                "trashPoint": player.trashPoint
            }, to=i)


   



    


def test_seed():
    
    for i in range(10):
        print(Seed.next_range(10,50))
    
    for i in range(10):
        print(Seed.next_float())

test_seed()
def test_boardstate():
    board = [
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
    [0, 0, 0, 0]
    ] 
    # board = [[2, 2, 2, 2],[2, 2, 2, 2],[2, 2, 2, 2],[2, 2, 2, 2]]
    print(BoardState.spawnTile(board))

#test_boardstate()
def test_move():               
    board = [
    [2, 2, 2, 2],
    [0, 2, 0, 2],
    [4, 0, 4, 0],
    [2, 0, 0, 2]
    ]
    
    #print(moveTile.transform(board))
    #print(moveTile.up(board))
    #print(moveTile.down(board))
    #print(moveTile.left(board))
    print(moveTile.right(board))
    

    # board = [
    # [2, 2, 2, 2],
    # [0, 0, 0, 0],
    # [0, 0, 0, 0],
    # [0, 0, 0, 0]
    # ]
    # print(moveTile.left(board))
              
# test_move()

if __name__ == '__main__':
    print(players_dict,"hello")
    print(Seed)
    socketio.run(app, debug=True)