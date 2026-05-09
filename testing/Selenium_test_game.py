import sys
import os
import time
import random
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from multiprocessing import Process, Queue
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from game2048.models import User
from game2048 import create_app, db
from config import SeleniumTestConfig


SLEEP_TIME = 2
TEST_TIME = 180
BASE_URL = "http://127.0.0.1:5000"
BOT1_EMAIL = "test@gmail.com"
BOT2_EMAIL = "tester1@gmail.com"
PASSWORD = "123456789"


@pytest.fixture(scope="session")
def app():

    app = create_app(SeleniumTestConfig)

    with app.app_context():
        db.drop_all()
        db.create_all()

        bot1 = User(
            username="tester",
            email="test@gmail.com",
            profile_pic="https://api.dicebear.com/9.x/croodles/svg?seed=tester&flip=true&backgroundColor=FFFFFF",
            elo=1000,
        )
        bot1.set_password("123456789")

        bot2 = User(
            username="another",
            email="tester1@gmail.com",
            profile_pic="https://api.dicebear.com/9.x/croodles/svg?seed=another&flip=true&backgroundColor=FFFFFF",
            elo=100,
        )
        bot2.set_password("123456789")

        db.session.add(bot1)
        db.session.add(bot2)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


# driver
def create_driver(incognito=False):
    options = Options()
    # options.add_argument("--headless")
    options.add_argument("--no-sandbox")

    prefs = {
        "profile.password_manager_leak_detection": False,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
    }

    options.add_experimental_option("prefs", prefs)

    if incognito:
        options.add_argument("--incognito")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )


# test actions
# addition register for test bot
def register_bot(driver, email, username):
    driver.get(f"{BASE_URL}/register")

    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "email").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    driver.find_element(By.ID, "confirm_password").send_keys(PASSWORD)

    driver.find_element(By.NAME, "submit").submit()

    time.sleep(SLEEP_TIME)


def login(driver, email, password):
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    time.sleep(SLEEP_TIME)
    driver.find_element(By.NAME, "submit").submit()


def create_game_and_get_code(driver):
    driver.find_element(By.ID, "createMatch").click()
    time.sleep(SLEEP_TIME)
    code = driver.find_element(By.ID, "matchID").text
    print(f"[Bot1] Game code: {code}")
    return code


def join_game_with_code(driver, code):
    print("[Bot2] Waiting for match input field...")
    input_box = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "match_id"))
    )

    input_box.clear()
    input_box.send_keys(code)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "submit"))
    ).click()
    print("[Bot2] Submitted join request")


def start_game(driver):
    try:
        driver.find_element(By.ID, "start_game").click()
    except Exception:
        pass
    driver.find_element(By.TAG_NAME, "body").click()


def play(driver, duration=TEST_TIME):
    move = ActionChains(driver)
    end_time = time.time() + duration
    while time.time() < end_time:
        direction = random.choice(["w", "a", "s", "d"])
        skill = random.choice(["i", "j", "k", "l"])
        move.send_keys(direction).perform()
        if random.random() > 0.75:
            move.send_keys(skill).perform()
        time.sleep(0.1)


def wait_for_home_ready(driver):
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "createMatch"))
    )


# make bot and login
def bot1_worker(queue):
    driver = create_driver(incognito=False)
    try:
        driver.get(BASE_URL)
        login(driver, BOT1_EMAIL, PASSWORD)
        print("[Bot1] Current URL:", driver.current_url)
        time.sleep(SLEEP_TIME)

        code = create_game_and_get_code(driver)
        queue.put(code)
        time.sleep(SLEEP_TIME)

        start_game(driver)
        play(driver)
    finally:
        driver.quit()


def bot2_worker(queue):
    driver = create_driver(incognito=True)
    try:
        driver.get(BASE_URL)
        login(driver, BOT2_EMAIL, PASSWORD)
        wait_for_home_ready(driver)
        print("[Bot2] Current URL:", driver.current_url)

        print("[Bot2] Waiting for game code...")
        code = queue.get()
        print(f"[Bot2] Received code: {code}")

        join_game_with_code(driver, code)
        time.sleep(SLEEP_TIME)

        start_game(driver)
        play(driver)
    finally:
        driver.quit()


# testing the bot can login and enter the game
def test_bot1_can_login_and_create_game(app):
    queue = Queue()
    driver = create_driver(incognito=False)

    try:
        driver.get(BASE_URL)
        login(driver, BOT1_EMAIL, PASSWORD)
        wait_for_home_ready(driver)

        code = create_game_and_get_code(driver)
        queue.put(code)

        assert code, "Game code should not be empty"
        print(f"[test_bot1] Game code: {code}")

    # finally is used for clean up no matter the result of the try statement
    finally:
        driver.quit()


def test_bot2_can_login_and_join_game(app):
    queue = Queue()
    p1 = Process(target=bot1_worker, args=(queue,))
    p1.start()
    # time for creating the game, avoid can not find element
    time.sleep(SLEEP_TIME)

    driver = create_driver(incognito=True)
    try:
        driver.get(BASE_URL)
        login(driver, BOT2_EMAIL, PASSWORD)
        wait_for_home_ready(driver)

        code = queue.get(timeout=30)
        assert code, "Should receive a valid game code from Bot1"

        join_game_with_code(driver, code)
        print(f"[test_bot2] Successfully joined game: {code}")

    # finally is used for clean up no matter the result of the try statement
    finally:
        driver.quit()
        p1.terminate()
        p1.join()


# bot create and start the game test
def test_multiplayer_game_full_session(app):
    queue = Queue()

    p1 = Process(target=bot1_worker, args=(queue,))
    p2 = Process(target=bot2_worker, args=(queue,))

    p1.start()
    p2.start()

    p1.join(timeout=TEST_TIME + 30)
    p2.join(timeout=TEST_TIME + 30)

    assert not p1.is_alive(), "Bot1 process did not finish in time"
    assert not p2.is_alive(), "Bot2 process did not finish in time"
