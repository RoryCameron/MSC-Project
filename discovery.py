"""
File: discovery.py
Author: Rory Cameron
Date: 23/06/2025
Description: Automates the discovery and sending of prompts and their corrosponding responses
"""


# ============ Imports ============
import os
import time
import json
from dotenv import load_dotenv

import openai

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import argparse
import re
import sys
# =================================



# ============ Load enviroment variables ============
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment")
# ===================================================



# ============ Initialize OpenAI client ============
client = openai.OpenAI(api_key=api_key)
# ==================================================



# ============ Functions ============


# Launches headless chrome browser via Selenium and returns rendered DOM
def get_rendered_dom(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(url)
    time.sleep(5)  
    
    dom = driver.page_source
    return dom, driver


# Extracts & parses JSON object from string (LLM output) 
def extract_json_from_text(text):
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in GPT output")
    json_str = text[start:end+1].strip('` \n')
    return json.loads(json_str)


# Sends prompt containing webpage DOM snapchat to LLM for chatbot selector extraction
def get_selectors_from_gpt(dom):
    print("Analyzing DOM with GPT to find chatbot selectors...")
    prompt = f"""
You're a security tester analyzing the DOM of a webpage. 
From the given DOM, extract a JSON object specifying:

- input_selector: CSS selector string for the chatbot user input field.
- send_selector: CSS selector string for the chatbot send button.
- response_selector: CSS selector string for the container holding chatbot responses.

DOM snapshot:
{dom[:8000]}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful web automation expert."},
            {"role": "user", "content": prompt}
        ]
    )
    
    raw = response.choices[0].message.content
    print("Raw GPT output:\n", raw)
    
    selectors = extract_json_from_text(raw)
    print("Extracted selectors:", selectors)
    return selectors


# Automates sending message to chatbot and returns latest bot reply
def send_message_and_get_response(driver, selectors, message, timeout=10):
    input_selector = selectors["input_selector"]
    send_selector = selectors["send_selector"]
    response_selector = selectors["response_selector"]

    # Find input field and enter message
    input_elem = driver.find_element("css selector", input_selector)
    input_elem.clear()
    input_elem.send_keys(message)

    # Click the send button
    send_btn = driver.find_element("css selector", send_selector)
    send_btn.click()

    # Reference the response container
    response_container = driver.find_element("css selector", response_selector)

    # Count bot messages before sending message
    bot_messages_before = response_container.find_elements("css selector", ".bot-message")
    count_before = len(bot_messages_before)

    # Wait until number of bot messages increases (i.e., new bot reply appears)
    WebDriverWait(driver, timeout).until(
        lambda d: len(d.find_element("css selector", response_selector)
                      .find_elements("css selector", ".bot-message")) > count_before
    )

    bot_messages_after = response_container.find_elements("css selector", ".bot-message")
    latest_bot_message = bot_messages_after[-1].text.strip()

    return latest_bot_message
# ===================================



# ============ Main Execution ============
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prompt Injection Script - Discovery Phase")
    parser.add_argument("url", help="URL of the chatbot page (e.g. http://127.0.0.1:5000/)")
    args = parser.parse_args()

    url = args.url

    # Error handling for URL
    if not re.match(r"^https?://", url):
        print(f"Error: '{url}' is not a valid URL. Make sure it starts with http:// or https://")
        sys.exit(1)

    user_message = "What flowers do you sell?"  # Message is hardcoded for now

    try:
        dom, driver = get_rendered_dom(url)
        selectors = get_selectors_from_gpt(dom)

        print(f"Sending message: {user_message}")
        bot_response = send_message_and_get_response(driver, selectors, user_message)
        print("Chatbot responded:", bot_response)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass
# ========================================