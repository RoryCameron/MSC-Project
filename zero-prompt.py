"""
File: promptInjector.py
Author: Rory Cameron
Date: 23/06/2025
Description: Main CLI entry point
Script overview:
- LLM discovers input selectors via discovery.py
- Seed prompt from prompts-dev.csv are injected, assigned yes to tested
- responses are scored via scorer.py, responses and scores etc stored in responses.csv
- ====== Unsure yet ======
- responses.csv sent to mutator.py to mutate new prompts based on scores?
- mutated prompts sent to optimizor.py to suggest best next prompts?
- new prompts added to prompts-dev.csv assigned no to tested?
- process repeats?
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
import os

from bayesian.scorer import score_response_with_llm
# =================================



# Lol
init(autoreset=True)
def print_banner():
    ascii_art = pyfiglet.figlet_format("ZeroPrompt", font="slant")
    print("\n\n" + Fore.CYAN + ascii_art + "\n\n")



# =========== Load untested prompts ===========
def load_untested_prompts(file_path):
    prompts = []
    try:
        with open(file_path, mode='r', encoding='utf-8-sig', errors='replace') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row.get("tested", "no").lower() != "yes" and row.get("prompt"):
                    prompts.append({
                        "category": row.get("category", "unknown"),
                        "prompt": row["prompt"]
                    })
        return prompts
    except Exception as e:
        print(Fore.RED + f"Failed to load prompts from CSV: {e}")
        sys.exit(1)
# =============================================



# ============ Mark prompts as tested ============
def mark_prompts_as_tested(used_prompts, file_path, used_scores): # Not most efficient using 2 parallel arrays but works for now
    updated_rows = []
    try:
        with open(file_path, mode='r', encoding='utf-8-sig', errors='replace') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if row["prompt"] in used_prompts:
                    idx = used_prompts.index(row["prompt"])
                    row["tested"] = "yes"
                    row["score"] = str(used_scores[idx])
                updated_rows.append(row)

        with open(file_path, mode='w', newline='', encoding='utf-8') as outfile:
            fieldnames = ["category", "prompt", "origin", "tested","score"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in updated_rows:
                writer.writerow(row)

    except Exception as e:
        print(Fore.RED + f"Failed to update prompts as tested: {e}")
# ================================================



# ============ Reset seed prompts only ============
def reset_seed_prompts(file_path):
    updated_rows = []
    try:
        with open(file_path, mode='r', encoding='utf-8-sig', errors='replace') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                if row.get("origin") == "seed":
                    row["tested"] = "no"
                    row["score"] = ""
                    updated_rows.append(row)

        with open(file_path, mode='w', newline='', encoding='utf-8') as outfile:
            fieldnames = ["category", "prompt", "origin", "tested", "score"]
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in updated_rows:
                writer.writerow(row)
        print(Fore.GREEN + "Seed prompts have been reset")

    except Exception as e:
        print(Fore.RED + f"Failed to reset seed prompts: {e}")
# =================================================



# ============ Reset responses.csv ============
def reset_responses(file_path="responses.csv"):
    try:
        os.remove(file_path)
        print(Fore.GREEN + "Responses have been reset")
    except Exception as e:
        print(Fore.RED + f"Failed to reset responses.csv: {e}")
# =============================================



# ============ Load seed prompts from csv ============
# LEGACY
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

    file_path = "prompts-dev.csv" # SEED + PROMPTS CSV

    if "--reset" in sys.argv:
        reset_seed_prompts(file_path)
        reset_responses()
        sys.exit(1)

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

        print(Fore.GREEN + "Successfully found selectors")


        # ============ Injection function ============
        def injection_phase():

            print(Fore.CYAN + "\nINJECTION PHASE\n")

            prompts = load_untested_prompts(file_path)
            if not prompts:
                print(Fore.RED + "No untested prompts found in prompts.csv.")
                return

            tested_prompts = []
            tested_scores = []

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
                        tested_prompts.append(prompt_text)
                        tested_scores.append(score)

                    except Exception as e:
                        print(Fore.RED + f"[Error {i}] Failed to inject prompt: {e}")
                        writer.writerow([category, prompt_text, str(e), 0, "Injection failed"])

                    print("=" * 60 + "\n\n")

                mark_prompts_as_tested(tested_prompts, file_path, tested_scores)

        injection_phase()

        # LEGACY
        """
        csv_file = "prompts.csv" # Initial seed file, this shouldnt change
        prompts = load_prompts_from_csv(csv_file)

        # Iterates through prompt dataset, sends prompt and gets response, then scores response via LLM and scorer prompt, records results to response dataset
        # this prompt file however should change to the new mutated prompts, with responses resetting each time?
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
        """


    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()
    

if __name__ == "__main__":
    main()
# ========================================