import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import unittest
from unittest.mock import patch, MagicMock, ANY

from game2048 import create_app
from config import TestConfig

from game2048.email import send_email, send_password_reset_email


class TestEmail(unittest.TestCase):
    # set up the application for test
    def setUp(self):
        self.app = create_app(TestConfig)

        self.app_context = self.app.app_context()
        self.app_context.push()
    
    # tear the application 
    def tearDown(self):
        self.app_context.pop()

    @patch("game2048.email.Message")
    @patch("game2048.email.Thread")
    def test_send_email(self, mock_thread, mock_message):
        send_email(
            subject="test",
            recipients=["tester@test.com"],
            text_body="text",
            html_body="html",
            sender="test@gmail.com",
        )
        # ensure the fake message is call successfully
        mock_message.assert_called_once_with(
            "test",
            sender="test@gmail.com",
            recipients=["tester@test.com"],
            body="text",
            html="html",
        )
        # ensure the fake thread is created and started successfully
        mock_thread.assert_called_once_with(target=ANY, args=ANY)
        mock_thread.return_value.start.assert_called_once()

    @patch("game2048.email.send_email")
    @patch("game2048.email.render_template")
    def test_send_password_reset_email(self, mock_render, mock_send):
        fake_user = MagicMock()

        fake_user.email = "test@test.com"
        fake_user.get_reset_password_token.return_value = "token"

        mock_render.side_effect = ["text", "html"]
        send_password_reset_email(fake_user)
        mock_send.assert_called_once_with(
            "[2048 Battle] Reset your Password", ["test@test.com"], "text", "html"
        )


if __name__ == "__main__":
    unittest.main()
