import random
import string
import threading
import time
from enum import Enum
from typing import TypedDict, Literal
# from game2048 import socketio

# ----------------------------------------------------------------
# Enums and Type Annotations
# ----------------------------------------------------------------


class MatchStatus(Enum):
    PENDING = "pending"
    START = "start"
    ONGOING = "ongoing"
    END = "end"


class TypeMatch(TypedDict):
    sids: dict[str, str]
    host: str
    opponent: str | None
    status: MatchStatus
    winner: str | None
    loser: str | None
    cells: dict[str, list]
    score: dict[str, int]
    hidden_score: dict[str, int]
    trash_point: dict[str, int]
    dead: dict[str, bool]
    random_array: list
    random_array_index: dict[str, int]
    timer: int


class TypeMove(TypedDict):
    match_id: str
    type: Literal["move"]
    direction: Literal["left", "right", "up", "down"]


class TypeAttack(TypedDict):
    match_id: str
    type: Literal["attack"]
    attack_id: str


# ----------------------------------------------------------------
# Match Game Logic
# ----------------------------------------------------------------


class MatchRandom:
    def __init__(self, seed=None, buffer_size=100):
        self.buffer_size = buffer_size
        self.rng = random.Random(seed)
        self.random_array = [self.rng.random() for _ in range(buffer_size)]
        self.index = 0

    def get_array(self):
        return self.random_array

    def get_index(self):
        return self.index

    def _next_random(self):
        value = self.random_array[self.index]
        self.index = (self.index + 1) % self.buffer_size
        return value

    def next_int(self):
        return int(self._next_random() * (2**31 - 1))

    def next_float(self):
        return self._next_random()

    def next_range(self, start, end):
        if start >= end:
            raise ValueError("start must be less than end")

        range_size = end - start
        return start + int(self._next_random() * range_size)

    def choice(self, array):
        if not array:
            raise IndexError("Cannot choose from an empty array")
        return array[self.next_range(0, len(array))]

    def randomPickEmpty(self, cell):
        N = len(cell)
        empty_space = []

        for r in range(N):
            for c in range(N):
                if cell[r][c] == 0:
                    empty_space.append([r, c])

        if len(empty_space) == 0:
            return None, None

        pick = self.next_range(0, len(empty_space))
        r, c = empty_space[pick]
        print([r, c])
        return [r, c]

    def randomPickNonEmpty(self, cell):
        N = len(cell)
        non_empty_space = []

        for r in range(N):
            for c in range(N):
                if cell[r][c] > 0:
                    non_empty_space.append([r, c])

        if len(non_empty_space) == 0:
            return None, None

        pick = self.next_range(0, len(non_empty_space))
        r, c = non_empty_space[pick]
        print([r, c])
        return [r, c]

    def fisher_yates_shuffle(self, array):
        for i in range(len(array) - 1, 0, -1):
            j = self.next_range(0, i + 1)
            array[i], array[j] = array[j], array[i]
        return array


class MatchTimer:
    def __init__(self, callback, args=[], duration=180):
        self.duration = duration
        self.callback = callback
        self.args = args
        self.has_start = False

        self.timer = None
        self.end_time = None

    def create(self):
        if self.timer:
            return self

        self.timer = threading.Timer(self.duration, self.callback, args=self.args)
        return self

    def start(self):
        if self.has_start:
            return self

        self.end_time = time.time() + self.duration
        self.timer.start()
        self.has_start = True

    def remaining(self):
        if self.end_time is None:
            return self.duration

        return max(0, self.end_time - time.time())


class BoardLogic:
    @staticmethod
    def compress(row):
        new = []
        for i in row:
            if i != 0:
                new.append(i)
        return new

    @staticmethod
    def merge(row):
        score = 0
        for i in range(len(row) - 1):
            if row[i] == row[i + 1]:
                row[i] = row[i] * 2
                row[i + 1] = 0

                score += row[i]
            elif row[i] < 0 or row[i + 1] < 0:
                s = row[i] + row[i + 1]
                if s == 0:
                    row[i] = 0
                    row[i + 1] = 0
        return row, score

    @staticmethod
    def left(cell):
        new_cell = []
        Total_score_for_move = 0
        moved = False

        for r in cell:
            row = BoardLogic.compress(r)
            row, score = BoardLogic.merge(row)
            row = BoardLogic.compress(row)

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
        new_cell, moved, Total_score_for_move = BoardLogic.left(reverse_cell)
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
            # print(new_array)
            new_cell.append(new_array)
        return new_cell

    @staticmethod
    def up(cell):
        Total_score_for_move = 0
        moved = False

        cell = BoardLogic.transform(cell)
        # print(cell)
        cell2 = []
        for c in cell:
            column = BoardLogic.compress(c)
            column, score = BoardLogic.merge(column)
            column = BoardLogic.compress(column)

            length = len(c) - len(column)

            for i in range(length):
                column.append(0)

            if c != column:
                moved = True
            # print(column)
            cell2.append(column)
            # for l in range(len(column)):
            #     new_cell[l].append(column[l])

            Total_score_for_move += score
        # print(cell2)
        new_cell = BoardLogic.transform(cell2)
        # print(cell2)
        return new_cell, moved, Total_score_for_move

    @staticmethod
    def down(cell):
        Total_score_for_move = 0
        moved = False
        cell = BoardLogic.transform(cell)
        print(cell)
        cell2 = []
        for c in cell:
            c = c[::-1]
            column = BoardLogic.compress(c)
            column, score = BoardLogic.merge(column)
            column = BoardLogic.compress(column)

            length = len(c) - len(column)

            for i in range(length):
                column.append(0)

            if c != column:
                moved = True
            # print(column)
            column = column[::-1]
            cell2.append(column)
            Total_score_for_move += score
        # print(cell2)
        new_cell = BoardLogic.transform(cell2)
        # print(cell2)
        return new_cell, moved, Total_score_for_move

    @staticmethod
    def hasMove(cell):
        N = len(cell)
        for r in range(N):
            for c in range(N):
                if cell[r][c] == 0:
                    return True
                if c < N - 1 and cell[r][c] == cell[r][c + 1]:
                    return True
                if r < N - 1 and cell[r][c] == cell[r + 1][c]:
                    return True
                if c < N - 1 and (cell[r][c] + cell[r][c + 1]) <= 0:
                    return True
                if r < N - 1 and (cell[r][c] + cell[r + 1][c]) <= 0:
                    return True
        return False


class BoardAction:
    @staticmethod
    def spawnTile(cell, match_random: MatchRandom):
        r, c = match_random.randomPickEmpty(cell)

        if r is None or c is None:
            return cell

        probability = match_random.next_float()
        if probability < 0.9:
            cell[r][c] = 2
        else:
            cell[r][c] = 4

        return cell

    @staticmethod
    def destroySpecificTile(cell, match_random: MatchRandom):
        r, c = match_random.randomPickNonEmpty(cell)
        if r is None or c is None:
            return cell, False

        cell[r][c] = 0
        return cell, True

    @staticmethod
    def createRandomTile(cell, match_random: MatchRandom):
        r, c = match_random.randomPickEmpty(cell)
        if r is None or c is None:
            return cell, False
        cell[r][c] = 2 ** match_random.next_range(1, 7)
        return cell, True

    @staticmethod
    def rearrangeBoard(cell, match_random: MatchRandom):
        N = len(cell)
        values = []

        for r in range(N):
            for c in range(N):
                if cell[r][c] > 0:
                    values.append(cell[r][c])
                    cell[r][c] = 0

        values = match_random.fisher_yates_shuffle(values)

        empty = []
        for r in range(N):
            for c in range(N):
                if cell[r][c] == 0:
                    empty.append([r, c])

        empty = match_random.fisher_yates_shuffle(empty)

        for i in range(len(values)):
            r, c = empty[i]
            cell[r][c] = values[i]

        return cell

    @staticmethod
    def makeRandomNegativeTile(cell, match_random: MatchRandom):
        r, c = match_random.randomPickEmpty(cell)
        if r is None or c is None:
            return cell, False
        cell[r][c] = (-1) * 2 ** match_random.next_range(1, 4)
        return cell, True


class MatchState:
    def __init__(self):
        self.matches: dict[str, TypeMatch] = {}
        self.matches_random: dict[str, dict[str, MatchRandom]] = {}
        self.matches_timer: dict[str, MatchTimer] = {}

    def get_match_by_id(self, id):
        match = self.matches.get(id)
        return match

    def create_match(self, host_username):
        match_id = self.__generate_match_id()
        match_random = MatchRandom(match_id)
        match_timer = MatchTimer(self.__end_game, [match_id])

        random_array = match_random.get_array()
        time_remaining = match_timer.create().remaining()

        match = {
            "sids": {host_username: ""},
            "host": host_username,
            "opponent": None,
            "status": MatchStatus.PENDING.value,
            "winner": None,
            "loser": None,
            "cells": {
                host_username: [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
            },
            "score": {host_username: 0},
            "hidden_score": {host_username: 0},
            "trash_point": {host_username: 0},
            "dead": {host_username: False},
            "random_array": random_array,
            "random_array_index": {host_username: 0},
            "timer": time_remaining,
        }

        self.matches[match_id] = match
        self.matches_random[match_id] = {host_username: match_random}
        self.matches_timer[match_id] = match_timer
        return (match_id, match)

    def join_match(self, match_id, opponent_username):
        match = self.get_match_by_id(match_id)

        if match is None:
            return None

        match_random = MatchRandom(match_id)
        self.matches_random[match_id][opponent_username] = match_random

        match["sids"][opponent_username] = ""
        match["opponent"] = opponent_username
        match["cells"][opponent_username] = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ]
        match["score"][opponent_username] = 0
        match["hidden_score"][opponent_username] = 0
        match["trash_point"][opponent_username] = 0
        match["dead"][opponent_username] = False
        match["random_array_index"][opponent_username] = 0

        return match

    def start_match(self, match_id):
        match = self.get_match_by_id(match_id)

        if match is None:
            return None

        player1 = match["host"]
        player2 = match["opponent"]

        player1_match_random = self.matches_random[match_id][player1]
        player2_match_random = self.matches_random[match_id][player2]

        BoardAction.spawnTile(match["cells"][player1], player1_match_random)
        BoardAction.spawnTile(match["cells"][player1], player1_match_random)

        BoardAction.spawnTile(match["cells"][player2], player2_match_random)
        BoardAction.spawnTile(match["cells"][player2], player2_match_random)

        self.__sync_random_index(match_id)

        return match

    def handle_action(self, match_id, username, data: TypeMove | TypeAttack):
        match = self.get_match_by_id(match_id)

        if match is None or not self.__is_player_input_valid(data):
            return None

        if data["type"] == "move":
            self.__handle_player_direction(match_id, match, username, data)

        if data["type"] == "attack":
            pass

        self.__sync_random_index(match_id)
        return match

    def __is_player_input_valid(self, data: TypeMove | TypeAttack):
        is_valid = False
        type_move_keys = ["match_id", "type", "direction"]
        type_attack_keys = ["match_id", "type", "attack_id"]

        if all(key in data for key in type_move_keys) or all(
            key in data for key in type_attack_keys
        ):
            is_valid = True

        if data["type"] == "move" and data["direction"] not in [
            "left",
            "right",
            "up",
            "down",
        ]:
            is_valid = False

        return is_valid

    def __handle_player_direction(
        self, match_id, match: TypeMatch, username, data: TypeMove | TypeAttack
    ):
        moved = False
        score = 0

        if data["direction"] == "left":
            match["cells"][username], moved, score = BoardLogic.left(
                match["cells"][username]
            )
        elif data["direction"] == "right":
            match["cells"][username], moved, score = BoardLogic.right(
                match["cells"][username]
            )
        elif data["direction"] == "up":
            match["cells"][username], moved, score = BoardLogic.up(
                match["cells"][username]
            )
        elif data["direction"] == "down":
            match["cells"][username], moved, score = BoardLogic.down(
                match["cells"][username]
            )

        BoardAction.spawnTile(
            match["cells"][username], self.matches_random[match_id][username]
        )
        match["score"][username] += score
        if match["hidden_score"][username] > 128:
            match["trash_point"][username] += 1
            match["hidden_score"][username] -= 128
        if not BoardLogic.hasMove(match["cells"][username]):
            match["dead"][username] = True

    def __sync_random_index(self, match_id):
        match = self.get_match_by_id(match_id)

        for username, m_random in self.matches_random[match_id].items():
            match["random_array_index"][username] = m_random.get_index()

    def __generate_match_id(self):
        characters = string.ascii_letters + string.digits

        while True:
            code = "".join(random.choices(characters, k=5))

            if code not in self.matches:
                return code

    def __end_game(self, match_id):
        print("END: ", match_id)


match_state = MatchState()
