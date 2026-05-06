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


# --- Config ---
TEST_TIME = 180
BASE_URL = "http://127.0.0.1:5000"
BOT1_EMAIL = "test@gmail.com"
BOT2_EMAIL = "tester1@gmail.com"
PASSWORD = "123456789"


# --- Driver Factory ---
def create_driver(incognito=False):
    options = Options()
    options.add_argument("--no-sandbox")
    if incognito:
        options.add_argument("--incognito")
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


# --- Bot Actions ---
def login(driver, email, password):
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    time.sleep(0.5)
    driver.find_element(By.NAME, "submit").submit()


def create_game_and_get_code(driver):
    driver.find_element(By.ID, "createMatch").click()
    time.sleep(1)
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
        direction = random.choice(['w', 'a', 's', 'd'])
        move.send_keys(direction).perform()
        time.sleep(0.1)


def wait_for_home_ready(driver):
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "createMatch"))
    )


# --- Worker Processes ---
def bot1_worker(queue):
    driver = create_driver(incognito=False)
    try:
        driver.get(BASE_URL)
        login(driver, BOT1_EMAIL, PASSWORD)
        print("[Bot1] Current URL:", driver.current_url)
        time.sleep(10)

        code = create_game_and_get_code(driver)
        queue.put(code)
        time.sleep(2)

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
        time.sleep(2)

        start_game(driver)
        play(driver)
    finally:
        driver.quit()


# --- Pytest Tests ---
def test_bot1_can_login_and_create_game():
    """Bot1 logs in, creates a game, and retrieves a game code."""
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
    finally:
        driver.quit()


def test_bot2_can_login_and_join_game():
    """Bot2 logs in and joins a game created by Bot1 (via shared queue)."""
    queue = Queue()

    p1 = Process(target=bot1_worker, args=(queue,))
    p1.start()

    # Give Bot1 time to create the game
    time.sleep(12)

    driver = create_driver(incognito=True)
    try:
        driver.get(BASE_URL)
        login(driver, BOT2_EMAIL, PASSWORD)
        wait_for_home_ready(driver)

        code = queue.get(timeout=30)
        assert code, "Should receive a valid game code from Bot1"

        join_game_with_code(driver, code)
        print(f"[test_bot2] Successfully joined game: {code}")
    finally:
        driver.quit()
        p1.terminate()
        p1.join()


def test_multiplayer_game_full_session():
    """
    Full integration test: Bot1 creates a game, Bot2 joins,
    both bots play for the configured TEST_TIME duration.

    Run with:
        pytest test_game2048.py::test_multiplayer_game_full_session -v -s
    """
    queue = Queue()

    p1 = Process(target=bot1_worker, args=(queue,))
    p2 = Process(target=bot2_worker, args=(queue,))

    p1.start()
    p2.start()

    p1.join(timeout=TEST_TIME + 30)
    p2.join(timeout=TEST_TIME + 30)

    assert not p1.is_alive(), "Bot1 process did not finish in time"
    assert not p2.is_alive(), "Bot2 process did not finish in time"