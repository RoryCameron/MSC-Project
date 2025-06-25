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

from bayesian.scorer import score_response_with_llm
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
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row and row.get("prompt"):
                    prompts.append({
                        "category": row["category"],
                        "prompt": row["prompt"]
                    })
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

        csv_file = "prompts.csv" # CSV file
        prompts = load_prompts_from_csv(csv_file)

        """
        # ============ TEMPERARY TESTING OF PROMPT INJECTION ============
        # Iterates through seed prompt dataset
        # Likely will have to remove/change for BO implementation
        
        for i, item in enumerate(prompts, 1):
            category = item["category"]
            prompt_text = item["prompt"]

            print("=" * 60)
            print(Fore.CYAN + f"[Prompt {i}] Category: {category}")
            print(Fore.YELLOW + f"Submitted Prompt: {prompt_text}")

            try:
                response = send_message_and_get_response(driver, selectors, prompt_text)
                print(Fore.CYAN + f"[Response {i}]")
                print(response)
            except Exception as e:
                print(Fore.RED + f"[Error {i}] Failed to inject prompt: {e}")

            print("=" * 60 + "\n\n")
        """

        with open("responses.csv", mode="a", newline='', encoding="utf-8") as logfile:
            writer = csv.writer(logfile)
            writer.writerow(["category", "prompt", "response", "score", "explanation"])

            for i, item in enumerate(prompts, 1):
                category = item["category"]
                prompt_text = item["prompt"]

                print("=" * 60)
                print(Fore.CYAN + f"[Prompt {i}] Category: {category}")
                print(Fore.YELLOW + f"Submitted Prompt: {prompt_text}")

                try:
                    response = send_message_and_get_response(driver, selectors, prompt_text)
                    print(Fore.CYAN + f"[Response {i}]")
                    print(response)

                    score, explanation = score_response_with_llm(prompt_text, response)
                    print(Fore.MAGENTA + f"[Score {i}] {score}")
                    print(Fore.LIGHTBLACK_EX + explanation)

                    writer.writerow([category, prompt_text, response, score, explanation])

                except Exception as e:
                    print(Fore.RED + f"[Error {i}] Failed to inject prompt: {e}")
                    writer.writerow([category, prompt_text, str(e), 0, "Injection failed"])

                print("=" * 60 + "\n\n")


    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()
    

if __name__ == "__main__":
    main()
# ========================================