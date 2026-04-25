import random
import string
import threading
import time
from enum import Enum
from typing import TypedDict
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


class MatchState:
    def __init__(self):
        self.matches: dict[str, TypeMatch] = {}
        self.matches_random: dict[str, dict[str, MatchRandom]] = {}
        self.matches_timer: dict[str, MatchTimer] = {}

    def get_match_by_id(self, id):
        match = self.matches.get(id)
        return match

    def create_match(self, host_username, host_sid):
        match_id = self.__generate_match_id()
        match_random = MatchRandom(match_id)
        match_timer = MatchTimer(self.__end_game, [match_id])

        random_array = match_random.get_array()
        time_remaining = match_timer.create().remaining()

        match = {
            "sids": {host_username: host_sid},
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

    def join_match(self, match_id, opponent_username, opponent_sid):
        match = self.get_match_by_id(match_id)

        if match is None:
            return None

        match_random = MatchRandom(match_id)
        self.matches_random[match_id][opponent_username] = match_random

        match["sids"][opponent_username] = opponent_sid
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

    def __generate_match_id(self):
        characters = string.ascii_letters + string.digits

        while True:
            code = "".join(random.choices(characters, k=5))

            if code not in self.matches:
                return code

    def __end_game(self, match_id):
        print("END: ", match_id)


match_state = MatchState()
match_id, match = match_state.create_match("jack", "1jk2jk31j2kjk1")
match_state.join_match(match_id, "John", "jks82881")
test = match_state.get_match_by_id(match_id)
print(test)
print(match_id)
