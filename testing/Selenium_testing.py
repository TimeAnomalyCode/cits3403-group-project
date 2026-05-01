import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from game2048.models import User

# from selenium.webdriver.common.credential import Credential
import time

SLEEP_TIME = 5
# Setup driver
# ChromeDriverManager().install() => it find the matching/correct version of Chrome
# Service(path_to_webdriver) => making the driver into an object
# webdriver.Chrome() => call the chrome browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Open website
# driver.get("https://www.google.com")
driver.get("http://127.0.0.1:5000")


# tested: login, logout, change username, change password(login),reset password(logout) (NOTE: only 4 feature)
# no test: create account(having email verification issue), ,
class test:
    def __init__(self, email, password, username, new_username, new_password):
        self.email = email
        self.password = password
        self.username = username
        self.new_username = new_username
        self.new_password = new_password
        self.user = User(id=1)

        pass

    def test_login(self):
        # find the input box and insert
        email = driver.find_element(By.NAME, "email")
        password = driver.find_element(By.NAME, "password")
        submit_button = driver.find_element(By.NAME, "submit")
        email.send_keys(self.email)  # "test@gmail.com"
        password.send_keys(self.password)  # "123456789"
        time.sleep(SLEEP_TIME)
        submit_button.submit()

    def test_logout(self):
        logout_button = driver.find_element(By.CLASS_NAME, "btn")
        logout_button.click()

    def test_profile(self):

        # driver.get("http://127.0.0.1:5000/profile/john")
        # time.sleep(SLEEP_TIME)
        profile_picture = driver.find_elements(By.ID, "profilePic")
        # print(profile_picture)
        time.sleep(SLEEP_TIME)
        profile_picture[0].click()

    def test_change_username(self):
        change_username = driver.find_elements(By.CLASS_NAME, "btn")
        # print(change_username)
        # for i in change_username:
        #     print(i)
        time.sleep(SLEEP_TIME)
        change_username[1].click()

        # submission process
        new_username = driver.find_element(By.NAME, "new_username")
        confirm_password = driver.find_element(By.NAME, "password")
        submit_button = driver.find_element(By.NAME, "submit")
        new_username.send_keys(self.new_username)  # "tester"
        confirm_password.send_keys(self.password)  # "123456789"
        time.sleep(SLEEP_TIME)
        submit_button.submit()
        self.username, self.new_username = self.new_username, self.username

    def test_change_password(self):
        change_password = driver.find_elements(By.CLASS_NAME, "btn")
        # print(change_username)
        # for i in change_password:
        #     print(i)
        time.sleep(SLEEP_TIME)
        change_password[2].click()

        # submission process
        current_password = driver.find_element(By.NAME, "current_password")
        new_password = driver.find_element(By.NAME, "new_password")
        confirm_password = driver.find_element(By.NAME, "confirm_password")

        current_password.send_keys(self.password)  # "123456789"
        new_password.send_keys(self.new_password)  # "12345678"
        confirm_password.send_keys(self.new_password)  # "12345678"

        time.sleep(SLEEP_TIME)
        submit_button = driver.find_element(By.NAME, "submit")
        submit_button.submit()
        self.password, self.new_password = self.new_password, self.password

    def test_back_to_home_page(self):
        home_icon = driver.find_elements(By.NAME, "homepage")
        home_icon[0].click()

    def test_forget_password(self):
        time.sleep(SLEEP_TIME)
        driver.get("http://127.0.0.1:5000/reset_password_request")
        time.sleep(SLEEP_TIME)

        enter_email = driver.find_element(By.ID, "email")
        enter_email.send_keys("example@example.com")
        time.sleep(SLEEP_TIME)

        token = self.user.get_reset_password_token()
        print(token)

        # reset password url
        driver.get(f"http://127.0.0.1:5000/reset_password/{token}")
        time.sleep(SLEEP_TIME)
        time.sleep(SLEEP_TIME)

        reset_password_old = driver.find_element(By.NAME,"password")
        reset_password_old.send_keys(self.new_password)

        reset_password_new = driver.find_element(By.NAME,"confirm_password")
        reset_password_new.send_keys(self.new_password)
        
        time.sleep(SLEEP_TIME)
        self.password, self.new_password = self.new_password ,self.password
        reset_password_button = driver.find_element(By.NAME, "submit")
        reset_password_button.click()



def test_process():
    test1 = test("test@gmail.com", "123456789", "tester", "john", "12345678")

    # ensure correct testing environment
    test1.test_logout()

    test1.test_login()
    time.sleep(SLEEP_TIME)

    test1.test_profile()
    time.sleep(SLEEP_TIME)

    test1.test_back_to_home_page()
    time.sleep(SLEEP_TIME)

    test1.test_profile()
    time.sleep(SLEEP_TIME)

    test1.test_change_username()
    time.sleep(SLEEP_TIME)

    test1.test_change_password()  # kicked out
    time.sleep(SLEEP_TIME)

    # == changed name and password ==
    # == reset environment ==
    test1.test_login()
    time.sleep(SLEEP_TIME)

    test1.test_profile()
    time.sleep(SLEEP_TIME)

    test1.test_change_username()
    time.sleep(SLEEP_TIME)

    test1.test_change_password()  # kicked out
    time.sleep(SLEEP_TIME)

    test1.test_login()
    time.sleep(SLEEP_TIME)

    test1.test_logout()
    time.sleep(SLEEP_TIME)


# test_process()
def testing_reset_pw():
    test1 = test("test@gmail.com", "123456789", "tester", "john", "12345678")
    test1.test_forget_password()
    time.sleep(SLEEP_TIME)
    test1.test_login()
    time.sleep(SLEEP_TIME)
    test1.test_logout()
    time.sleep(SLEEP_TIME)
    test1.test_forget_password()
    time.sleep(SLEEP_TIME)


testing_reset_pw()
# Close browser
driver.quit()
