import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from game2048 import create_app, db
from game2048.models import User
from config import TestConfig


class TestUserModel(unittest.TestCase):

    # set up the application and make the initial database for test
    def setUp(self):
        self.app = create_app(TestConfig)

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        self.user = User(username="tester", email="tester@test.com", profile_pic="test.png")

        self.user.set_password("password")

        db.session.add(self.user)
        db.session.commit()


    # tear the application and database down after testing to ensure proper remove of test data 
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        
        db.engine.dispose()
        self.app_context.pop()
        

    


    def test_set_password(self):
        self.user.set_password("password")

        self.assertFalse(self.user.password_hash == "password")


    def test_check_password(self):
        self.user.set_password("password")
        self.assertTrue(self.user.check_password("password"))

        self.assertFalse(self.user.check_password("wrong"))


    def test_get_reset_password_token(self):
        token = self.user.get_reset_password_token()

        self.assertIsNotNone(token)


    def test_verify_reset_password_token(self):
        token = self.user.get_reset_password_token()

        verified_user = User.verify_reset_password_token(token)
        self.assertEqual(verified_user.id, self.user.id)


if __name__ == "__main__":
    unittest.main()