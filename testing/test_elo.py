import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest

from game2048 import create_app, db
from game2048.models import User, Match
from game2048.elo import (
    expected,
    getMatchCount,
    getK,
    update_elo,
)

from config import TestConfig


class TestEloFunctions(unittest.TestCase):
    # set up the application for test
    def setUp(self):
        self.app = create_app(TestConfig)

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Create test users
        self.user1 = User(
            username="player1",
            email="p1@test.com",
            profile_pic="default.png",
            elo=1000,
        )

        self.user1.set_password("password")

        self.user2 = User(
            username="player2",
            email="p2@test.com",
            profile_pic="default.png",
            elo=1000,
        )

        self.user2.set_password("password")

        db.session.add(self.user1)
        db.session.add(self.user2)
        db.session.commit()
        
        # tear the application and database down after testing to ensure proper remove of test data
        def tearDown(self):
            db.session.remove()
            db.drop_all()

            db.engine.dispose()
            self.app_context.pop()

    def test_expected_same_elo(self):
        result = expected(1000, 1000)

        self.assertAlmostEqual(
            result,
            0.5,
            places=2,
            msg="Players with same ELO should have 0.5 expected score"
        )

    def test_expected_higher_elo(self):
        result = expected(1200, 1000)

        self.assertLess(
            result,
            0.5,
            "Higher rated player currently produces expected value below 0.5"
        )


    def test_getK_with_new_player(self):
        result = getK(5)

        self.assertEqual(
            result,
            40,
            "Players with less than 15 matches should have K=40"
        )

    def test_getK_with_intermediate_player(self):
        result = getK(20)

        self.assertEqual(
            result,
            20,
            "Players with 15-29 matches should have K=20"
        )

    def test_getK_with_experienced_player(self):
        result = getK(40)

        self.assertEqual(
            result,
            10,
            "Players with 30+ matches should have K=10"
        )

    def test_getMatchCount_without_matches(self):
        count = getMatchCount(self.user1.id)

        self.assertEqual(
            count,
            0,
            "New player should initially have 0 matches"
        )

    def test_getMatchCount_with_matches(self):

        match1 = Match(
            player1_id=self.user1.id,
            player2_id=self.user2.id,
            player1_elo=1000,
            player2_elo=1000,
        )

        match2 = Match(
            player1_id=self.user2.id,
            player2_id=self.user1.id,
            player1_elo=1000,
            player2_elo=1000,
        )

        db.session.add(match1)
        db.session.add(match2)
        db.session.commit()

        count = getMatchCount(self.user1.id)

        self.assertEqual(
            count,
            2,
            "getMatchCount() should count all matches involving player"
        )


    def test_update_elo_change(self):

        new_winner_elo, new_loser_elo = update_elo(
            self.user1,
            self.user2
        )
        # test increase
        self.assertGreater(
            new_winner_elo,
            self.user1.elo,
            "Winner ELO should increase after victory"
        )
        # test decrease
        self.assertLess(
            new_loser_elo,
            self.user2.elo,
            "Loser ELO should decrease after defeat"
        )

    def test_update_elo_with_same_level(self):

        new_winner_elo, new_loser_elo = update_elo(
            self.user1,
            self.user2
        )

        self.assertEqual(
            new_winner_elo,
            1020,
            "Winner should gain 20 ELO against equal opponent"
        )

        self.assertEqual(
            new_loser_elo,
            980,
            "Loser should lose 20 ELO against equal opponent"
        )


if __name__ == "__main__":
    unittest.main()