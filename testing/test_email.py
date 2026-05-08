# unittest is used
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock, ANY
from game2048.email import send_email, send_password_reset_email, render_template


class Testemail(unittest.TestCase):

    #filename.method/function/object name
    # @patch("game2048.email.mail.send")
    # def test_send_async_email(self, send_mock): #set up a fake object to record the work of the function
    #     # create fake variable
    #     fake_app = MagicMock()
    #     fake_msg = MagicMock()

    #     # if see "with" syntax, it should have "__enter__" and "__exit__" to mimic the with syntax behavior 
    #     # fake_app.app_context.return_value.__enter__.return_value = None
    #     # fake_app.app_context.return_value.__exit__.return_value = None

    #     send_async_email(fake_app, fake_msg)

    #     send_mock.asset_called_once_with(fake_msg)

    @patch("game2048.email.Message")
    @patch("game2048.email.Thread")
    def test_send_email(self, mock_thread, mock_message):
       
        # faking passing parameters
        send_email(
        subject = "test",
        recipients = ["tester"],
        text_body= "text",
        html_body= "html",
        sender="test@gamil.com"
        )

        # faking "msg" and check called
        mock_message.assert_called_once_with(
            "test",
            sender="test@gamil.com",
            recipients = ["tester"],
            body= "text",
            html= "html",
            
        ) 
        
        # faking to create a thread and check it is created
        mock_thread.assert_called_once_with(target=ANY,args=ANY) # use ANY when don't know how to make parameter
        mock_thread.return_value.start.assert_called_once()
        
    @patch("game2048.email.send_email")
    @patch("game2048.email.render_template")
    def test_send_password_reset_email(self,mock_render, mock_send):
        
        # create fake user
        fake_user = MagicMock()
        
        # create fake user attribute
        fake_user.email = "test@test.com"
        fake_user.get_reset_password_token.return_value = "token"

        # using a fake render_template to make .txt and .html
        mock_render.side_effect = ["text","html"]
        
        # call the actual function
        send_password_reset_email(fake_user)
        
        # using a fake send_email to mimic action
        mock_send.assert_called_once_with(
            "[2048 Battle] Reset your Password",
            [fake_user.email],
            "text", 
            "html"
        )

        

