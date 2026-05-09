import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest

from game2048 import create_app, db
from config import TestConfig


class TestRoutes(unittest.TestCase):
    # set up the application for test
    def setUp(self):
        self.app = create_app(TestConfig)

        self.client = self.app.test_client()

        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    # tear the application
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        db.engine.dispose()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.client.get("/register")
        self.assertEqual(response.status_code, 200)

    def test_reset_password_page(self):
        response = self.client.get("/reset_password_request")
        self.assertEqual(response.status_code, 200)

    def test_invalid_page(self):
        response = self.client.get("/does-not-exist")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
