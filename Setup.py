from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
import time
import random
from Config import USERNAME, PASSWORD, NAVBLUE_URL
from Utils import slow_type

def create_stealth_driver():
    """
    Creates a Selenium WebDriver instance with stealth settings to avoid detection.

    Returns:
        WebDriver: An undetected Chrome WebDriver configured with stealth options.
    """
    options = uc.ChromeOptions()
    options.headless = True
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return uc.Chrome(options=options)

def login_to_navblue(driver):
    """
    Logs into the Navblue portal using provided credentials and waits for the main menu.

    Args:
        driver (WebDriver): An active Selenium WebDriver session, already created.
    """
    driver.get(NAVBLUE_URL)
    time.sleep(random.uniform(2,4))
    print("Logging in...")
    slow_type(driver.find_element(By.ID, 'MasterMain_txtUserName'), USERNAME)
    time.sleep(random.uniform(0.5, 1.2))
    slow_type(driver.find_element(By.ID, 'MasterMain_txtPassword'), PASSWORD)
    driver.find_element(By.ID, 'MasterMain_txtPassword').send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'linkMenu')))
    print("Logged in...")