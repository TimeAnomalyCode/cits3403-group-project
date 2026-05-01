import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from game2048 import app
from game2048.errors import not_found_error, internal_error
from flask import render_template
from unittest.mock import patch, MagicMock, ANY

class TestError(unittest.TestCase):

    def setUp(self):
        self.app = app   
        self.app.testing = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
    
    def test_not_found_error(self):
        server_response = self.client.get("/this-page-does-not-exist")
        self.assertEqual(server_response.status, '404 NOT FOUND')
        self.assertIn(b'Something has gone wrong!', server_response.data)
    
    # no need to test code 500
    # def test_internal_error(self): # should test status code 500
    #     server_response = self.client.get("/trigger-error")
    #     self.assertEqual(server_response.status,'404 NOT FOUND')
    #     self.assertIn(b'wrong!', server_response.data)

if __name__ == "__main__":
    print("Starting tests...")
    unittest.main()