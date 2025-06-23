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
from prompt_injector import send_message_and_get_response

import pyfiglet
from colorama import init, Fore, Style

import csv
# =================================



# Lol
init(autoreset=True)
def print_banner():
    ascii_art = pyfiglet.figlet_format("ZeroPrompt", font="slant")
    print("\n\n" + Fore.CYAN + ascii_art + "\n\n")



# ============ Load seed prompts from csv ============
def load_prompts_from_csv(file_path):
    prompts = []
    try:
        with open(file_path, mode='r', encoding='utf-8-sig', errors='replace') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            for row in reader:
                if row:
                    prompts.append(row[0])
        return prompts
    except Exception as e:
        print(Fore.RED + f"Failed to load prompts from CSV: {e}")
        sys.exit(1)
# ====================================================



# ============ Main Execution ============

def main():

    print_banner()

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
        print(Fore.CYAN + "\nDISCOVERY PHASE\n")

        print("Discovering selectors...")
        selectors = discover_selectors(driver, url)

        if not selectors:
            print(Fore.RED + "Failed to discover any selectors")

        # print(f"Selectors discovered: {selectors}")
        print(Fore.GREEN + "Successfully found selectors")

        message = "What flowers do you sell?"

        print(Fore.CYAN + "\nINJECTION PHASE\n")
        # ============ TEMPERARY TESTING OF PROMPT INJECTION ============
        # print(f"Sending message: {message}")

        # response = send_message_and_get_response(driver, selectors, message)
        # print(f"Chatbot responded: {response}")

        csv_file = "seed-prompts.csv"
        prompts = load_prompts_from_csv(csv_file)

        for i, prompt in enumerate(prompts, 1):
            print(("="*60))
            print(Fore.CYAN + f"[Prompt {i}] {prompt}")
            try:
                response = send_message_and_get_response(driver, selectors, prompt)
                print(f"[Response {i}] {response}")
            except Exception as e:
                print(Fore.RED + f"[Error {i}] Failed to inject prompt: {e}")
            print(("="*60) + "\n\n")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
# ========================================