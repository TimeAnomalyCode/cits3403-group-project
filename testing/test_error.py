import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from game2048 import create_app
from config import TestConfig


class TestErrorPages(unittest.TestCase):

    # set up the application for test
    def setUp(self):
        self.app = create_app(TestConfig)

        self.client = self.app.test_client()

        self.app_context = self.app.app_context()
        self.app_context.push()

    # tear the application 
    def tearDown(self):
        self.app_context.pop()


    def test_404_error(self):
        response = self.client.get( "/this-page-does-not-exist")

        self.assertEqual(response.status_code, 404)


    def test_404_contains_message(self):
        response = self.client.get("/this-page-does-not-exist")

        self.assertIn(b"Something has gone wrong!", response.data)


if __name__ == "__main__":
    unittest.main()