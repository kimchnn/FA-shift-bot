from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

def slow_type(element, text):
    """
    Types text one character at a time with random delays to simulate human-like typing. To help avoid bot detection.

    Args:
        element (WebElement): The input or text field to type into.
        text (str): The full string to be typed character by character.
    """

    for char in text:
        element.send_keys(char)
        time.sleep(random.uniform(0.05, 0.15))


def get_shadow_element(driver, host_element, selector):
    """
    Returns the nested element from within a shadow DOM.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        host_element (WebElement): The shadow host element that contains the shadow DOM.
        selector (str): The CSS selector to locate the desired element inside the shadow root.

    Returns:
        WebElement or None: The matched element inside the shadow root, or None if not found.
    """
    return driver.execute_script(
        "return arguments[0]?.shadowRoot?.querySelector(arguments[1])", host_element, selector
    )


def wait_for_shadow_selector(driver, host, selector, timeout=20):
    """
    Wait for a selector to exist inside a shadowRoot
    
    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        host (WebElement): The shadow host element that contains the shadow root.
        selector (str): The CSS selector for the element inside the shadow root.
        timeout (int, optional): Maximum time to wait in seconds. Defaults to 20.

    Returns:
        WebElement: The located element inside the shadow root.

    """
    js = """
    const host = arguments[0];
    const sel = arguments[1];
    if (!host || !host.shadowRoot) return null;
    return host.shadowRoot.querySelector(sel);
    """
    end_time = time.time() + timeout
    while time.time() < end_time:
        el = driver.execute_script(js, host, selector)
        if el:
            return el
        time.sleep(0.3)
    raise TimeoutError(f"Timeout: '{selector}' not found in shadow root.")

def traverse_open_time_page(driver):
    # Step 1: Wait for <x-open-times>
    x_open_times_host = WebDriverWait(driver, 90).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'x-open-times'))
    )
    print("✅ <x-open-times> found")

    # Step 2: x-ot-daily
    x_ot_daily = wait_for_shadow_selector(driver, x_open_times_host, 'x-ot-daily', timeout=30)
    print("✅ <x-ot-daily> found")

    # Step 3: x-open-time-page
    x_open_time_page = wait_for_shadow_selector(driver, x_ot_daily, 'x-open-time-page', timeout=30)
    print("✅ <x-open-time-page> found")
    