import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock, ANY
from game2048.models import User
from game2048 import app
from werkzeug.security import generate_password_hash, check_password_hash

class TestUser(unittest.TestCase):
    
    def setUp(self):
        # This typically means that you attempted to use functionality that needed
        # the current application. To solve this, set up an application context
        # with app.app_context(). See the documentation for more information.
        self.app = app   
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.user = User(id=1)
   
    
    def test_set_password(self):
        self.user.set_password("test")
        self.assertTrue(check_password_hash(self.user.password_hash, "test"))
        

    def test_check_password(self):
        self.user.set_password("test")
        self.assertTrue(self.user.check_password('test')) 

    def test_get_reset_password_token(self):
        self.assertTrue(self.user.get_reset_password_token())
    
    def test_verify_reset_password_token(self):
        token = self.user.get_reset_password_token()
        
        # JWT need a id for it to look up the user
        self.assertEqual(self.user, User.verify_reset_password_token(token))


if __name__ == "__main__":
    print("Starting tests...")
    unittest.main()