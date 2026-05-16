import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest

from game2048.board import (
    MatchRandom,
    BoardLogic,
    BoardAction,
    MatchState,
    MatchStatus,
)
from game2048 import create_app

# test move
class TestBoardLogic(unittest.TestCase):
    
    # test compress
    def test_compress_removes_zeros(self):
        row = [2, 0, 2, 4]

        result = BoardLogic.compress(row)

        self.assertEqual(
            result,
            [2, 2, 4],
            "compress() should remove zeros"
        )

    def test_compress_all_zeros(self):
        row = [0, 0, 0, 0]

        result = BoardLogic.compress(row)

        self.assertEqual(
            result,
            [],
            "compress() should return empty list if all zeros"
        )

    def test_compress_no_zeros(self):
        row = [2, 4, 8]

        result = BoardLogic.compress(row)

        self.assertEqual(
            result,
            [2, 4, 8],
            "compress() should not modify row without zeros"
        )

    # test merge
    def test_merge_single_pair(self):
        row = [2, 2]

        merged_row, score = BoardLogic.merge(row)

        self.assertEqual(
            merged_row,
            [4, 0],
            "merge() should combine equal tiles"
        )

        self.assertEqual(
            score,
            4,
            "merge() should correctly calculate score"
        )

    def test_merge_double_pair(self):
        row = [2, 2, 4, 4]

        merged_row, score = BoardLogic.merge(row)

        self.assertEqual(
            merged_row,
            [4, 0, 8, 0],
            "merge() should merge multiple pairs"
        )

        self.assertEqual(
            score,
            12,
            "merge() should sum all merge scores"
        )

    def test_merge_triple_tiles(self):
        row = [2, 2, 2]

        merged_row, score = BoardLogic.merge(row)

        self.assertEqual(
            merged_row,
            [4, 0, 2],
            "merge() should only merge first matching pair"
        )

    def test_merge_negative_cancel(self):
        row = [-2, 2]

        merged_row, score = BoardLogic.merge(row)

        self.assertEqual(
            merged_row,
            [0, 0],
            "Positive and negative tiles should cancel"
        )

        self.assertEqual(
            score,
            0,
            "Negative cancellation should not add to score"
        )

    def test_merge_no_matches(self):
        row = [2, 4, 8]

        merged_row, score = BoardLogic.merge(row)

        self.assertEqual(
            merged_row,
            [2, 4, 8],
            "merge() should not modify unmatched tiles"
        )

        self.assertEqual(
            score,
            0,
            "merge() should produce 0 score without merges"
        )

    # transform
    def test_transform(self):
        board = [
            [1, 2],
            [3, 4]
        ]

        result = BoardLogic.transform(board)

        self.assertEqual(
            result,
            [
                [1, 3],
                [2, 4]
            ],
            "transform() should transpose board"
        )
    
    # test directional move
    # left
    def test_left_merge(self):
        # should go all the way
        board = [
            [2, 0, 2, 0]
        ]

        new_board, moved, score = BoardLogic.left(board)

        self.assertEqual(
            new_board,
            [[4, 0, 0, 0]],
            "left() should merge left"
        )

        self.assertTrue(
            moved,
            "left() should report movement"
        )

        self.assertEqual(
            score,
            4,
            "left() should calculate score"
        )

    def test_left_no_movement(self):
        # no left move
        board = [
            [2, 4, 8, 16]
        ]

        new_board, moved, score = BoardLogic.left(board)

        self.assertEqual(
            new_board,
            board,
            "left() should not modify unchanged board"
        )

        self.assertFalse(
            moved,
            "left() should report no movement"
        )

        self.assertEqual(
            score,
            0,
            "left() should return 0 score without merges"
        )

    def test_left_merge_priority(self):
        # only the left most pair merges, the third tile stays and move left
        board = [[2, 2, 2, 0]]

        new_board, moved, score = BoardLogic.left(board)

        self.assertEqual(
            new_board,
            [[4, 2, 0, 0]],
            "left() should merge the leftmost matching pair first"
        )
        self.assertTrue(moved, "left() should report movement")
        self.assertEqual(score, 4, "left() should score only the merged pair")

    def test_left_multiple_rows(self):
        # merges many row
        board = [
            [4, 0, 4, 0],
            [2, 2, 0, 0],
            [0, 0, 0, 2],
            [8, 4, 2, 0],
        ]

        new_board, moved, score = BoardLogic.left(board)

        self.assertEqual(
            new_board,
            [
                [8, 0, 0, 0],
                [4, 0, 0, 0],
                [2, 0, 0, 0],
                [8, 4, 2, 0],
            ],
            "left() should merge and pack each row independently"
        )
        self.assertTrue(moved, "left() should report movement when any row changed")
        self.assertEqual(score, 12, "left() should sum score across all rows")

    def test_left_partial_movement(self):
        # one row is already full, the other is not
        board = [
            [2, 4, 8, 16],
            [2, 0, 2,  0],
        ]

        new_board, moved, score = BoardLogic.left(board)

        self.assertEqual(
            new_board,
            [
                [2, 4, 8, 16],
                [4, 0, 0,  0],
            ],
            "left() should only change rows that need moving"
        )
        self.assertTrue(moved, "left() should report movement when at least one row changed")
        self.assertEqual(score, 4, "left() should only score the row that merged")

    def test_left_negative_cancel(self):
        # move left cancel out
        board = [[-2, 2, 0, 0]]

        new_board, moved, score = BoardLogic.left(board)

        self.assertEqual(
            new_board,
            [[0, 0, 0, 0]],
            "left() should cancel a negative tile with its positive counterpart"
        )
        self.assertTrue(moved, "left() should report movement after a cancellation")
        self.assertEqual(score, 0, "left() should not score a negative cancellation")

    # right
    def test_right_merge(self):
        # should go all the way
        board = [
            [2, 0, 2, 0]
        ]

        new_board, moved, score = BoardLogic.right(board)

        self.assertEqual(
            new_board,
            [[0, 0, 0, 4]],
            "right() should merge right"
        )

        self.assertTrue(
            moved,
            "right() should report movement"
        )

        self.assertEqual(
            score,
            4,
            "right() should calculate score"
        )

    def test_right_no_movement(self):
        # no right move 
        board = [[0, 2, 4, 8]]

        new_board, moved, score = BoardLogic.right(board)

        self.assertEqual(
            new_board,
            [[0, 2, 4, 8]],
            "right() should not modify an already right-packed row"
        )
        self.assertFalse(moved, "right() should report no movement")
        self.assertEqual(score, 0, "right() should return zero score")

    def test_right_merge_priority(self):
        # the right most pair merges, the other move right accordingly
        board = [[0, 2, 2, 2]]

        new_board, moved, score = BoardLogic.right(board)

        self.assertEqual(
            new_board,
            [[0, 0, 2, 4]],
            "right() should merge the rightmost matching pair first"
        )
        self.assertTrue(moved, "right() should report movement")
        self.assertEqual(score, 4, "right() should score only the merged pair")

    def test_right_multiple_rows(self):
        # move many row
        board = [
            [0, 4, 0, 4],
            [0, 0, 2, 2],
            [2, 0, 0, 0],
            [0, 8, 4, 2],
        ]

        new_board, moved, score = BoardLogic.right(board)

        self.assertEqual(
            new_board,
            [
                [0, 0, 0, 8],
                [0, 0, 0, 4],
                [0, 0, 0, 2],
                [0, 8, 4, 2],
            ],
            "right() should merge and pack each row independently to the right"
        )
        self.assertTrue(moved, "right() should report movement")
        self.assertEqual(score, 12, "right() should sum score across all rows")

    def test_right_negative_cancel(self):
        # move right cancel out
        board = [[0, 0, -2, 2]]

        new_board, moved, score = BoardLogic.right(board)

        self.assertEqual(
            new_board,
            [[0, 0, 0, 0]],
            "right() should cancel a negative tile with its positive counterpart"
        )
        self.assertTrue(moved, "right() should report movement after a cancellation")
        self.assertEqual(score, 0, "right() should not score a negative cancellation")

    # up
    def test_up_merge(self):
        # move up 
        board = [
            [2, 0],
            [2, 0]
        ]

        new_board, moved, score = BoardLogic.up(board)

        self.assertEqual(
            new_board,
            [
                [4, 0],
                [0, 0]
            ],
            "up() should merge upward"
        )

        self.assertTrue(
            moved,
            "up() should report movement"
        )

        self.assertEqual(
            score,
            4,
            "up() should calculate score"
        )

    def test_up_no_movement(self):
        # no up move
        board = [
            [2,  4],
            [8, 16],
        ]

        new_board, moved, score = BoardLogic.up(board)

        self.assertEqual(
            new_board,
            [[2, 4], [8, 16]],
            "up() should not modify an already top-packed board"
        )
        self.assertFalse(moved, "up() should report no movement")
        self.assertEqual(score, 0, "up() should return zero score")

    def test_up_merge_priority(self):
        # top pair merges, third tile stays
        board = [
            [2, 0, 0, 0],
            [2, 0, 0, 0],
            [2, 0, 0, 0],
            [0, 0, 0, 0],
        ]

        new_board, moved, score = BoardLogic.up(board)

        self.assertEqual(
            new_board,
            [[4, 0, 0, 0], [2, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            "up() should merge the topmost matching pair in each column first"
        )
        self.assertTrue(moved, "up() should report movement")
        self.assertEqual(score, 4, "up() should score only the merged pair")

    def test_up_multiple_columns(self):
        # merges many row
        board = [
            [2, 0, 4,  8],
            [2, 0, 4,  0],
            [0, 0, 0,  0],
            [4, 0, 0,  8],
        ]

        new_board, moved, score = BoardLogic.up(board)

        self.assertEqual(
            new_board,
            [
                [ 4, 0, 8, 16],
                [ 4, 0, 0,  0],
                [ 0, 0, 0,  0],
                [ 0, 0, 0,  0],
            ],
            "up() should merge and pack each column independently upward"
        )
        self.assertTrue(moved, "up() should report movement")
        self.assertEqual(score, 28, "up() should sum score across all columns")

    def test_up_negative_cancel(self):
        # move up cancel out
        board = [
            [-2, 0],
            [ 2, 0],
        ]

        new_board, moved, score = BoardLogic.up(board)

        self.assertEqual(
            new_board,
            [[0, 0], [0, 0]],
            "up() should cancel a negative tile with its positive counterpart in the same column"
        )
        self.assertTrue(moved, "up() should report movement after a cancellation")
        self.assertEqual(score, 0, "up() should not score a negative cancellation")
    
    # down
    def test_down_merge(self):
        # move down
        board = [
            [2, 0],
            [2, 0]
        ]

        new_board, moved, score = BoardLogic.down(board)

        self.assertEqual(
            new_board,
            [
                [0, 0],
                [4, 0]
            ],
            "down() should merge downward"
        )

        self.assertTrue(
            moved,
            "down() should report movement"
        )

        self.assertEqual(
            score,
            4,
            "down() should calculate score"
        )

    def test_down_no_movement(self):
        # no move down
        board = [
            [ 8, 16],
            [ 2,  4],
        ]

        new_board, moved, score = BoardLogic.down(board)

        self.assertEqual(
            new_board,
            [[8, 16], [2, 4]],
            "down() should not modify an already bottom-packed board"
        )
        self.assertFalse(moved, "down() should report no movement")
        self.assertEqual(score, 0, "down() should return zero score")

    def test_down_merge_priority(self):
        # the bottom pair merges, the top tile stays
        board = [
            [0, 0, 0, 0],
            [2, 0, 0, 0],
            [2, 0, 0, 0],
            [2, 0, 0, 0],
        ]

        new_board, moved, score = BoardLogic.down(board)

        self.assertEqual(
            new_board,
            [[0, 0, 0, 0], [0, 0, 0, 0], [2, 0, 0, 0], [4, 0, 0, 0]],
            "down() should merge the bottommost matching pair in each column first"
        )
        self.assertTrue(moved, "down() should report movement")
        self.assertEqual(score, 4, "down() should score only the merged pair")

    def test_down_multiple_columns(self):
        # merges many row 
        board = [
            [2, 0, 4, 0],
            [2, 0, 4, 0],
            [0, 0, 0, 0],
            [4, 0, 0, 8],
        ]

        new_board, moved, score = BoardLogic.down(board)

        self.assertEqual(
            new_board,
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [4, 0, 0, 0],
                [4, 0, 8, 8],
            ],
            "down() should merge and pack each column independently downward"
        )
        self.assertTrue(moved, "down() should report movement")
        self.assertEqual(score, 12, "down() should sum score across all columns")

    def test_down_negative_cancel(self):
        # move down cancel out
        board = [
            [ 2, 0],
            [-2, 0],
        ]

        new_board, moved, score = BoardLogic.down(board)

        self.assertEqual(
            new_board,
            [[0, 0], [0, 0]],
            "down() should cancel a negative tile with its positive counterpart in the same column"
        )
        self.assertTrue(moved, "down() should report movement after a cancellation")
        self.assertEqual(score, 0, "down() should not score a negative cancellation")
    
    # test has move determination
    def test_hasMove_returns_true_for_empty_space(self):
        board = [
            [2, 0],
            [4, 8]
        ]

        result = BoardLogic.hasMove(board)

        self.assertTrue(
            result,
            "hasMove() should return True if empty space exists"
        )

    def test_hasMove_returns_true_for_horizontal_merge(self):
        board = [
            [2, 2],
            [4, 8]
        ]

        result = BoardLogic.hasMove(board)

        self.assertTrue(
            result,
            "hasMove() should return True if horizontal merge exists"
        )

    def test_hasMove_returns_true_for_vertical_merge(self):
        board = [
            [2, 4],
            [2, 8]
        ]

        result = BoardLogic.hasMove(board)

        self.assertTrue(
            result,
            "hasMove() should return True if vertical merge exists"
        )

    def test_hasMove_returns_false_when_no_moves_exist(self):
        board = [
            [2, 4],
            [8, 16]
        ]

        result = BoardLogic.hasMove(board)

        self.assertFalse(
            result,
            "hasMove() should return False when board is locked"
        )

    def test_hasMove_returns_true_for_horizontal_negative_cancel(self):
        # cell[0][0] + cell[0][1] = 2 + (-2) = 0 <= 0, so a move exists
        board = [
            [ 2, -2],
            [ 4,  8]
        ]

        result = BoardLogic.hasMove(board)

        self.assertTrue(
            result,
            "hasMove() should return True when adjacent horizontal tiles cancel to zero"
        )

    def test_hasMove_returns_true_for_vertical_negative_cancel(self):
        # cell[0][0] + cell[1][0] = 2 + (-2) = 0 <= 0, so a move exists
        board = [
            [ 2,  4],
            [-2,  8]
        ]

        result = BoardLogic.hasMove(board)

        self.assertTrue(
            result,
            "hasMove() should return True when adjacent vertical tiles cancel to zero"
        )


# test attack and spawn
class TestBoardAction(unittest.TestCase):
    # set up the seed random 
    def setUp(self):
        self.random = MatchRandom(seed=1)

    # test spawn tile
    def test_spawnTile_adds_single_tile(self):
        board = [
            [0, 0],
            [0, 0]
        ]

        BoardAction.spawnTile(board, self.random)

        non_zero_tiles = sum(
            1 for row in board for value in row if value != 0
        )

        self.assertEqual(
            non_zero_tiles,
            1,
            "spawnTile() should add exactly one tile"
        )

    def test_spawnTile_generates_valid_tile_value(self):
        board = [
            [0, 0],
            [0, 0]
        ]

        BoardAction.spawnTile(board, self.random)

        values = [
            value
            for row in board
            for value in row
            if value != 0
        ]

        self.assertIn(
            values[0],
            [2, 4],
            "spawnTile() should only generate 2 or 4"
        )

    def test_spawnTile_does_not_modify_full_board(self):
        board = [
            [2, 4],
            [8, 16]
        ]

        original_board = [row[:] for row in board]

        BoardAction.spawnTile(board, self.random)

        self.assertEqual(
            board,
            original_board,
            "spawnTile() should not modify a full board"
        )

        non_zero_tiles = sum(
            1 for row in board for value in row if value != 0
        )

        self.assertEqual(
            non_zero_tiles,
            4,
            "spawnTile() should not add any tile to a full board"
        )

    
    # test destroy tile
    def test_destroySpecificTile_removes_one_tile(self):
        board = [
            [2, 4],
            [8, 0]
        ]

        new_board, cost = BoardAction.destroySpecificTile(
            board,
            trash_point=5,
            match_random=self.random
        )

        non_zero_tiles = sum(
            1 for row in new_board for value in row if value != 0
        )

        self.assertEqual(
            non_zero_tiles,
            2,
            "destroySpecificTile() should remove one tile"
        )

        self.assertEqual(
            cost,
            4,
            "destroySpecificTile() should cost 4 points"
        )

    def test_destroySpecificTile_fails_without_points(self):
        board = [
            [2, 4],
            [8, 0]
        ]

        original_board = [row[:] for row in board]

        new_board, cost = BoardAction.destroySpecificTile(
            board,
            trash_point=0,
            match_random=self.random
        )

        self.assertEqual(
            new_board,
            original_board,
            "destroySpecificTile() should not modify board without enough points"
        )

        self.assertEqual(
            cost,
            0,
            "Failed attack should cost 0"
        )

    def test_destroySpecificTile_on_empty_board(self):
        board = [
            [0, 0],
            [0, 0]
        ]

        new_board, cost = BoardAction.destroySpecificTile(
            board,
            trash_point=5,
            match_random=self.random
        )

        self.assertEqual(
            new_board,
            board,
            "destroySpecificTile() should not modify empty board"
        )

        self.assertEqual(
            cost,
            0,
            "destroySpecificTile() should cost 0 on empty board"
        )

   
    # test create tile
    def test_createRandomTile_adds_one_tile(self):
        board = [
            [0, 0],
            [0, 0]
        ]

        new_board, cost = BoardAction.createRandomTile(
            board,
            trash_point=5,
            match_random=self.random
        )

        non_zero_tiles = sum(
            1 for row in new_board for value in row if value != 0
        )

        self.assertEqual(
            non_zero_tiles,
            1,
            "createRandomTile() should create one tile"
        )

        self.assertEqual(
            cost,
            1,
            "createRandomTile() should cost 1 point"
        )

    def test_createRandomTile_generates_power_of_two(self):
        board = [
            [0, 0],
            [0, 0]
        ]

        new_board, cost = BoardAction.createRandomTile(
            board,
            trash_point=5,
            match_random=self.random
        )

        values = [
            value
            for row in new_board
            for value in row
            if value != 0
        ]

        valid_values = [2, 4, 8, 16, 32, 64]

        self.assertIn(
            values[0],
            valid_values,
            f"createRandomTile() should generate a power-of-two in {valid_values} (128 is excluded)"
        )

    def test_createRandomTile_fails_without_points(self):
        board = [
            [0, 0],
            [0, 0]
        ]

        original_board = [row[:] for row in board]

        new_board, cost = BoardAction.createRandomTile(
            board,
            trash_point=0,
            match_random=self.random
        )

        self.assertEqual(
            new_board,
            original_board,
            "createRandomTile() should fail without enough points"
        )

        self.assertEqual(
            cost,
            0,
            "Failed attack should cost 0"
        )

    
    # test board rearrange
    def test_rearrangeBoard_preserves_values(self):
        board = [
            [2, 4],
            [8, 0]
        ]

        original_values = sorted([2, 4, 8])

        new_board, cost = BoardAction.rearrangeBoard(
            board,
            trash_point=5,
            match_random=self.random
        )

        new_values = sorted([
            value
            for row in new_board
            for value in row
            if value != 0
        ])

        self.assertEqual(
            new_values,
            original_values,
            "rearrangeBoard() should preserve tile values"
        )

        self.assertEqual(
            cost,
            4,
            "rearrangeBoard() should cost 4 points"
        )

    def test_rearrangeBoard_fails_without_points(self):
        board = [
            [2, 4],
            [8, 0]
        ]

        original_board = [row[:] for row in board]

        new_board, cost = BoardAction.rearrangeBoard(
            board,
            trash_point=0,
            match_random=self.random
        )

        self.assertEqual(
            new_board,
            original_board,
            "rearrangeBoard() should fail without enough points"
        )

        self.assertEqual(
            cost,
            0,
            "Failed attack should cost 0"
        )

    
    # test negative tile
    def test_makeRandomNegativeTile_creates_negative_tile(self):
        board = [
            [0, 0],
            [0, 0]
        ]

        new_board, cost = BoardAction.makeRandomNegativeTile(
            board,
            trash_point=5,
            match_random=self.random
        )

        negative_tiles = [
            value
            for row in new_board
            for value in row
            if value < 0
        ]

        self.assertEqual(
            len(negative_tiles),
            1,
            "makeRandomNegativeTile() should create one negative tile"
        )

        self.assertEqual(
            cost,
            2,
            "makeRandomNegativeTile() should cost 2 points"
        )

    def test_makeRandomNegativeTile_generates_valid_value(self):
        board = [
            [0, 0],
            [0, 0]
        ]

        new_board, cost = BoardAction.makeRandomNegativeTile(
            board,
            trash_point=5,
            match_random=self.random
        )

        negative_tiles = [
            value
            for row in new_board
            for value in row
            if value < 0
        ]

        self.assertIn(
            negative_tiles[0],
            [-2, -4, -8],
            "makeRandomNegativeTile() should generate valid negative tile"
        )

    def test_makeRandomNegativeTile_fails_without_points(self):
        board = [
            [0, 0],
            [0, 0]
        ]

        original_board = [row[:] for row in board]

        new_board, cost = BoardAction.makeRandomNegativeTile(
            board,
            trash_point=0,
            match_random=self.random
        )

        self.assertEqual(
            new_board,
            original_board,
            "makeRandomNegativeTile() should fail without enough points"
        )

        self.assertEqual(
            cost,
            0,
            "Failed attack should cost 0"
        )
    

# test player state
class TestMatchState(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.match_state = MatchState()
    
    def tearDown(self):
        for timer in self.match_state.matches_timer.values():
            if timer.timer is not None:
                timer.timer.cancel()
        self.app_context.pop()

    # test create match and its status 
    def test_create_match_creates_match(self):
        match_id, match = self.match_state.create_match("host")

        self.assertIsNotNone(
            match,
            "create_match() should create a match"
        )

    def test_create_match_sets_host(self):
        match_id, match = self.match_state.create_match("host")

        self.assertEqual(
            match["host"],
            "host",
            "create_match() should correctly assign host"
        )

    def test_create_match_sets_pending_status(self):
        match_id, match = self.match_state.create_match("host")

        self.assertEqual(
            match["status"],
            MatchStatus.PENDING.value,
            "New matches should start as pending"
        )

    def test_create_match_initializes_board(self):
        match_id, match = self.match_state.create_match("host")

        self.assertEqual(
            match["cells"]["host"],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            "create_match() should initialize empty board"
        )

    
    # test match id has corresponding match
    def test_get_match_by_id_returns_match(self):
        match_id, match = self.match_state.create_match("host")

        result = self.match_state.get_match_by_id(match_id)

        self.assertEqual(
            result,
            match,
            "get_match_by_id() should return correct match"
        )

    def test_get_match_by_id_invalid(self):
        result = self.match_state.get_match_by_id("invalid")

        self.assertIsNone(
            result,
            "get_match_by_id() should return None for invalid id"
        )

   
    # test match joining
    def test_join_match_adds_opponent(self):
        match_id, match = self.match_state.create_match("host")

        updated_match = self.match_state.join_match(
            match_id,
            "opponent"
        )

        self.assertEqual(
            updated_match["opponent"],
            "opponent",
            "join_match() should assign opponent"
        )

    def test_join_match_initializes_opponent_board(self):
        match_id, match = self.match_state.create_match("host")

        updated_match = self.match_state.join_match(
            match_id,
            "opponent"
        )

        self.assertEqual(
            updated_match["cells"]["opponent"],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [0, 0, 0, 0]
            ],
            "join_match() should initialize opponent board"
        )

    def test_join_match_invalid_match(self):
        result = self.match_state.join_match(
            "invalid",
            "opponent"
        )

        self.assertIsNone(
            result,
            "join_match() should return None for invalid match"
        )

   
    # test match starting
    def test_start_match_spawns_two_tiles(self):
        match_id, match = self.match_state.create_match("host")

        self.match_state.join_match(match_id, "opponent")

        updated_match = self.match_state.start_match(match_id)

        host_tiles = sum(
            1 for row in updated_match["cells"]["host"]
            for value in row
            if value != 0
        )

        opponent_tiles = sum(
            1 for row in updated_match["cells"]["opponent"]
            for value in row
            if value != 0
        )

        self.assertEqual(
            host_tiles,
            2,
            "start_match() should spawn two tiles for host"
        )

        self.assertEqual(
            opponent_tiles,
            2,
            "start_match() should spawn two tiles for opponent"
        )

    def test_start_match_invalid_match(self):
        result = self.match_state.start_match("invalid")

        self.assertIsNone(
            result,
            "start_match() should return None for invalid match"
        )


    # test handle general player action, including score change depending on valid move, invalid match state
    def test_handle_action_valid_move(self):
        match_id, match = self.match_state.create_match("host")
        self.match_state.join_match(match_id, "opponent")

        match["cells"]["host"] = [
            [2, 0, 2, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ]

        data = {
            "match_id": match_id,
            "type": "move",
            "direction": "left"
        }

        result = self.match_state.handle_action(
            match_id,
            "host",
            data
        )

        self.assertEqual(
            result["score"]["host"],
            4,
            "Valid move should increase score"
        )

    def test_handle_action_invalid_direction(self):
        match_id, match = self.match_state.create_match("host")

        data = {
            "match_id": match_id,
            "type": "move",
            "direction": "invalid"
        }

        result = self.match_state.handle_action(
            match_id,
            "host",
            data
        )

        self.assertIsNone(
            result,
            "Invalid direction should return None"
        )

    def test_handle_action_invalid_match(self):
        data = {
            "match_id": "invalid",
            "type": "move",
            "direction": "left"
        }

        result = self.match_state.handle_action(
            "invalid",
            "host",
            data
        )

        self.assertIsNone(
            result,
            "handle_action() should return None for invalid match"
        )

    def test_handle_action_dead_player(self):
        match_id, match = self.match_state.create_match("host")

        match["dead"]["host"] = True

        data = {
            "match_id": match_id,
            "type": "move",
            "direction": "left"
        }

        result = self.match_state.handle_action(
            match_id,
            "host",
            data
        )

        self.assertIsNone(
            result,
            "Dead players should not be able to act"
        )

    
    # test attack flag is reset
    def test_clear_attacks_resets_attack_flags(self):
        match_id, match = self.match_state.create_match("host")

        self.match_state.join_match(match_id, "opponent")

        match["is_attacked"]["host"] = "attack"
        match["is_attacked"]["opponent"] = "attack"

        self.match_state.clear_attacks(match_id)

        self.assertIsNone(
            match["is_attacked"]["host"],
            "clear_attacks() should reset host attack flag"
        )

        self.assertIsNone(
            match["is_attacked"]["opponent"],
            "clear_attacks() should reset opponent attack flag"
        )