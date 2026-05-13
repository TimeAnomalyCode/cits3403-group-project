import sys
import os
import time
import random
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from multiprocessing import Process, Queue, Event
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from game2048.models import User
from game2048 import create_app, db, socketio
from config import SeleniumTestConfig
import threading
import requests

SLEEP_TIME = 1
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
        
        flask_thread = threading.Thread(target=run_flask,args=(app,))
        flask_thread.daemon = True
        flask_thread.start()
        wait_for_server()

        yield app

        db.session.remove()
        db.drop_all()

def wait_for_server(url="http://127.0.0.1:5000", timeout=10):
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(url, timeout=0.5)
            if response.status_code == 200:
                return
        except requests.ConnectionError:
            time.sleep(0.05)
    raise RuntimeError(f"Flask server did not start within {timeout}s")


def run_flask(app):
    socketio.run(app, use_reloader=False, allow_unsafe_werkzeug=True)


# driver
def create_driver(incognito=False):
    options = Options()
    options.add_argument("--headless")
    # options.add_argument("--no-sandbox")

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
    code = driver.find_element(By.ID, "match_id").text
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

    print("trying to find button")

    try:
        start_btn = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "start_game"))
        )

        print("button exists")

        # move the view to focus and show find button
        driver.execute_script("arguments[0].scrollIntoView();", start_btn)

        time.sleep(1)

        driver.execute_script("arguments[0].click();", start_btn)

        print("clicked start")

    except Exception as e:
        print("START GAME ERROR:", e)


def play(driver, duration=TEST_TIME):
    print("playing", flush=True)
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
def bot1_worker(queue, ready, play_test=True):
    driver = create_driver(incognito=False)
    try:
        driver.get(BASE_URL)
        login(driver, BOT1_EMAIL, PASSWORD)
        print("[Bot1] Current URL:", driver.current_url)
        time.sleep(SLEEP_TIME)

        code = create_game_and_get_code(driver)
        queue.put(code)
        time.sleep(SLEEP_TIME)
        print("i am bot 1, ready to go")
        
        if play_test:
            start_game(driver)
            play(driver)
    finally:
        driver.quit()


def bot2_worker(queue, ready):
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
        print("i am bot 2, ready to go")

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
    ready = Event()
    p1 = Process(target=bot1_worker, args=(queue, ready, False))
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
        p1.join(timeout=15)
        assert p1.exitcode == 0
        p1.terminate()


# bot create and start the game test
def test_multiplayer_game_full_session(app):
    queue = Queue()
    ready = Event()
    p1 = Process(
        target=bot1_worker,
        args=(
            queue,
            ready,
        ),
    )
    p2 = Process(
        target=bot2_worker,
        args=(
            queue,
            ready,
        ),
    )

    p1.start()
    p2.start()

    p1.join(timeout=TEST_TIME + 30)
    p2.join(timeout=TEST_TIME + 30)

    assert p1.exitcode == 0, f"Bot1 process fail with {p1.exitcode}"
    assert p2.exitcode == 0, f"Bot2 process fail with{p2.exitcode}"


