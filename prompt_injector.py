"""
File: promptInjector.py
Author: Rory Cameron
Date: 23/06/2025
Description: Sends prompts to chatbots and gets response
"""


# ============ Imports ============
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException
)
import time
import sys
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
    bot_response_selector = selectors["bot_response_selector"]

    print("\nSELECTORS TEST\n")
    print(input_selector)
    print(send_selector)
    print(response_selector)
    print(bot_response_selector)
    

    toggle_state = selectors.get("toggle_state")

    if "toggle_selector" in selectors:
        
        try:

            if toggle_state == "closed":

                # Wait for and click toggle (with JavaScript click as fallback)
                toggle_button = WebDriverWait(driver, timeout).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selectors["toggle_selector"]))
                )
                try:
                    toggle_button.click()
                    toggle_state = "open"
                except:
                    driver.execute_script("arguments[0].click();", toggle_button)
                
                selectors["toggle_state"] = toggle_state

            # Combined wait for all critical elements
            WebDriverWait(driver, timeout).until(lambda d:
                d.find_element(By.CSS_SELECTOR, selectors["input_selector"]).is_displayed() and
                d.find_element(By.CSS_SELECTOR, selectors["send_selector"]).is_displayed() and
                d.find_element(By.CSS_SELECTOR, selectors["response_selector"]).is_displayed() and
                d.find_element(By.CSS_SELECTOR, selectors["bot_response_selector"]).is_displayed()
            )

            # Small pause for animations to complete
            time.sleep(0.5)

        except Exception as e:
            print(f"Error toggling chatbot: {str(e)}")
            driver.save_screenshot("toggle_error.png")
            raise

    input_selector = selectors["input_selector"]
    send_selector = selectors["send_selector"]
    response_selector = selectors["response_selector"]
    bot_response_selector = selectors["bot_response_selector"]
    #toggle_selector = selectors["toggle_selector"]
    #toggle_state = selectors["input_selector"]

    print("\nSELECTORS TEST\n")
    print(input_selector)
    print(send_selector)
    print(response_selector)
    print(bot_response_selector)
    #print(toggle_selector)
    
    # Input Prompt
    input_elem = driver.find_element("css selector", input_selector)
    input_elem.clear()
    input_elem.send_keys(message)

    # Send Prompt
    send_btn = driver.find_element("css selector", send_selector)

    response_container = driver.find_element("css selector", response_selector)
    bot_messages_before = response_container.find_elements("css selector", bot_response_selector)
    count_before = len(bot_messages_before)

    send_btn.click()
    # print("Submit Button Pressed")

    # print("Sleeping")
    # time.sleep(10)
    
    # Some chatbots dont add new elements for the chatbot, so need to see if anything new has changed at all
    # print("Attempting WebDriverWait . . . ")
    WebDriverWait(driver, timeout).until(
        lambda d: len(d.find_element("css selector", response_selector)
                      .find_elements("css selector", bot_response_selector)) > count_before
    )
    # print("Made it pased WebDriverWait")

    """
    lambda d: len(d.find_element("css selector", response_selector)
              .find_elements("css selector", bot_response_selector)) > count_before
    """

    response_container = driver.find_element("css selector", response_selector)
    bot_messages_after = response_container.find_elements("css selector", bot_response_selector)
    # print("Calcuated after element count")
    latest_bot_message = bot_messages_after[-1].text.strip()
    # print("Stripped Message")
    return latest_bot_message
# ===================================================================
