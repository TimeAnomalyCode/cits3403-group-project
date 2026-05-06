import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pytest
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from game2048.models import User

# from selenium.webdriver.common.credential import Credential
SLEEP_TIME = 0.5

@pytest.fixture
def driver():
    options = Options()
    # options.add_argument("--headless")  # uncomment for CI/no-display
    options.add_argument("--no-sandbox")

    # Setup driver
    # ChromeDriverManager().install() => it find the matching/correct version of Chrome
    # Service(path_to_webdriver) => making the driver into an object
    # webdriver.Chrome() => call the chrome browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # Open website
    # driver.get("https://www.google.com")
    driver.get("http://127.0.0.1:5000")
    
    yield driver  # test runs
    
    driver.quit() # Close browser


# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))


# driver.get("http://127.0.0.1:5000")


# tested: login, logout, change username, change password(login),reset password(logout) (NOTE: only 4 feature)
# no test: create account(having email verification issue), ,
class test:
    def __init__(self, driver, email, password, username, new_username, new_password):
        self.driver = driver
        self.email = email
        self.password = password
        self.username = username
        self.new_username = new_username
        self.new_password = new_password
        self.user = User(id=1)

        pass

    def test_login(self):
        self.driver.find_element(By.NAME, "email").send_keys(self.email)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        time.sleep(SLEEP_TIME)
        self.driver.find_element(By.NAME, "submit").submit()

    def test_logout(self):
        self.driver.find_element(By.CLASS_NAME, "btn").click()

    def test_profile(self):
        time.sleep(SLEEP_TIME)
        self.driver.find_elements(By.ID, "profilePic")[0].click()

    def test_change_username(self):
        time.sleep(SLEEP_TIME)
        self.driver.find_elements(By.CLASS_NAME, "btn")[1].click()
        self.driver.find_element(By.NAME, "new_username").send_keys(self.new_username)
        self.driver.find_element(By.NAME, "password").send_keys(self.password)
        time.sleep(SLEEP_TIME)
        self.driver.find_element(By.NAME, "submit").submit()
        self.username, self.new_username = self.new_username, self.username

    def test_change_password(self):
        time.sleep(SLEEP_TIME)
        self.driver.find_elements(By.CLASS_NAME, "btn")[2].click()
        self.driver.find_element(By.NAME, "current_password").send_keys(self.password)
        self.driver.find_element(By.NAME, "new_password").send_keys(self.new_password)
        self.driver.find_element(By.NAME, "confirm_password").send_keys(
            self.new_password
        )
        time.sleep(SLEEP_TIME)
        self.driver.find_element(By.NAME, "submit").submit()
        self.password, self.new_password = self.new_password, self.password

    def test_back_to_home_page(self):
        self.driver.find_elements(By.NAME, "homepage")[0].click()

    def test_forget_password(self):
        time.sleep(SLEEP_TIME)
        self.driver.get("http://127.0.0.1:5000/reset_password_request")
        time.sleep(SLEEP_TIME)
        self.driver.find_element(By.ID, "email").send_keys("example@example.com")
        time.sleep(SLEEP_TIME)

        token = self.user.get_reset_password_token()
        self.driver.get(f"http://127.0.0.1:5000/reset_password/{token}")
        time.sleep(SLEEP_TIME)

        self.driver.find_element(By.NAME, "password").send_keys(self.new_password)
        self.driver.find_element(By.NAME, "confirm_password").send_keys(
            self.new_password
        )
        time.sleep(SLEEP_TIME)
        self.password, self.new_password = self.new_password, self.password
        self.driver.find_element(By.NAME, "submit").click()



def test_process(driver):
    test1 = test(driver, "test@gmail.com", "123456789", "tester", "john", "12345678")

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
def testing_reset_pw(driver):
    test1 = test(driver,"test@gmail.com", "123456789", "tester", "john", "12345678")
    test1.test_forget_password()
    time.sleep(SLEEP_TIME)
    test1.test_login()
    time.sleep(SLEEP_TIME)
    test1.test_logout()
    time.sleep(SLEEP_TIME)
    test1.test_forget_password()
    time.sleep(SLEEP_TIME)


