"""
File: promptInjector.py
Author: Rory Cameron
Date: 23/06/2025
Description: Main CLI entry point
"""

# ============ Imports ============
import sys
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

from discovery import discover_selectors
from promptInjector import send_message_and_get_response
# =================================


# ============ Main Execution ============

def main():
    if len(sys.argv) < 2:
        print("Usage: python zeroPrompt.py <url>")
        sys.exit(1)

    url = sys.argv[1]

    if not re.match(r"^https?://", url):
        print("Invalid URL. Must start with http:// or https://")
        sys.exit(1)

    print(f"[+] Launching browser and loading URL: {url}")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        print("[+] Discovering selectors...")
        selectors = discover_selectors(driver, url)

        print(f"[+] Selectors discovered: {selectors}")

        message = "What flowers do you sell?"
        print(f"[+] Sending message: {message}")

        response = send_message_and_get_response(driver, selectors, message)
        print(f"[+] Chatbot responded: {response}")

    except Exception as e:
        print(f"[!] Error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
# ========================================