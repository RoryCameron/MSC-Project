"""
File: promptInjector.py
Author: Rory Cameron
Date: 23/06/2025
Description: Sends prompts to chatbots and gets response
"""


# ============ Imports ============
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
# =================================


# ============ Launch headless browser ============
def launch_browser(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    return driver
# =================================================



# ============ Send prompts to chatbot and get responses ============
def send_message_and_get_response(driver, selectors, message, timeout=10):
    input_selector = selectors["input_selector"]
    send_selector = selectors["send_selector"]
    response_selector = selectors["response_selector"]

    input_elem = driver.find_element("css selector", input_selector)
    input_elem.clear()
    input_elem.send_keys(message)

    send_btn = driver.find_element("css selector", send_selector)
    send_btn.click()

    response_container = driver.find_element("css selector", response_selector)

    bot_messages_before = response_container.find_elements("css selector", ".bot-message")
    count_before = len(bot_messages_before)

    WebDriverWait(driver, timeout).until(
        lambda d: len(d.find_element("css selector", response_selector)
                      .find_elements("css selector", ".bot-message")) > count_before
    )

    bot_messages_after = response_container.find_elements("css selector", ".bot-message")
    latest_bot_message = bot_messages_after[-1].text.strip()

    return latest_bot_message
# ===================================================================

