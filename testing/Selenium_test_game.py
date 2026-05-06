import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from multiprocessing import Process
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import random
# from selenium import webdriver

def random_input_keys():
    keys = ['w', 'a', 's','d']
    direction = random.choice(keys)
    return direction


def controller(name):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("http://127.0.0.1:5000")
    
    body = driver.find_element(By, "body")
    body.click() 

    move = ActionChains(driver)

    end_time = time.time() + 180

    while end_time > time.time():
        keyboard_input = random_input_keys()
        move.send_keys(keyboard_input).perform()
        time.sleep(0.1)


    driver.quit()

if __name__ == "__main__":
    
    process1 = Process(target=controller, args=("Bot1"))
    process2 = Process(target=controller, args=("Bot2"))

    actions = ActionChains(process1)

    process1.start()
    process2.start()

    process1.join()
    process2.join()