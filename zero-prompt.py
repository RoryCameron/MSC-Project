"""
File: promptInjector.py
Author: Rory Cameron
Date: 23/06/2025
Description: Main CLI entry point, Main execution loop contained here
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
from bayesian.optimizer import BayesianOptimizer

import pandas as pd
import numpy as np

from results import
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



# ============ Reset responses.csv ============
def reset_success(file_path="success_db.csv"):
    try:
        os.remove(file_path)
        print(Fore.GREEN + "Successes have been reset")
    except Exception as e:
        print(Fore.RED + f"Failed to reset success_db.csv: {e}")
# =============================================


# ============ Exists program after 3 successful prompts are found
def check_for_success(success_count):
    if os.path.exists("success_db.csv"):
        try:
            # Read CSV and handle headers if they exist
            success_df = pd.read_csv("success_db.csv")
                        
            # If no headers exist, the score will be in the last column
            if 'score' not in success_df.columns:
                success_df.columns = ['prompt', 'response', 'score'][:len(success_df.columns)]
                        
            # Convert scores to numeric, forcing invalid values to NaN
            success_df['score'] = pd.to_numeric(success_df['score'], errors='coerce')
                        
            # Count only valid scores >= 8 (drops NaN values)
            success_count = len(success_df[success_df['score'] >= 8].dropna())
        except Exception as e:
            print(f"Error reading success file: {e}")
            success_count = 0
    else:
        success_count = 0
                
    if success_count >= 3: # Change per testing
        print("\n=== TERMINATING - 3+ SUCCESSES FOUND ===") # Format Better
        sys.exit(0)

# ============ Main Execution ============

def main():
    
    file_path = "prompts-dev.csv" # SEED + PROMPTS CSV

    # Fix this to only 1 or 2 calls
    if "--reset" in sys.argv:
        reset_seed_prompts(file_path)
        reset_responses()
        reset_success()
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


        bo = BayesianOptimizer()

        for cycle in range(1, 21):  # Max 20 cycles
            print(Fore.CYAN + f"\nCYCLE {cycle}\n")
            
            # 1. Your existing injection phase
            injection_phase()

            # 2. Load responses
            # THIS SECTION BEEN ADDED
            try:
                responses = pd.read_csv("responses.csv")
                print(Fore.YELLOW + f"DEBUG: score column types before conversion:\n{responses.dtypes}\n")

                responses['score'] = pd.to_numeric(responses['score'], errors='coerce')
                print(Fore.YELLOW + f"DEBUG: score column types after conversion:\n{responses.dtypes}\n")

                responses = responses.dropna(subset=['score'])  # Clean any NaNs before comparison
            except FileNotFoundError:
                print("No responses found - skipping cycle")
                continue
            except Exception as e:
                print(Fore.RED + f"Failed to load/clean responses.csv: {e}")
                continue

            # 3. Process successes
            successes = responses[responses['score'] >= 8] # CHANGE VALUE FOR SUCCESS RATE

            if not successes.empty:
                # Write with header only if file doesn't exist
                write_header = not os.path.exists("success_db.csv")
                successes.to_csv("success_db.csv", 
                                mode='a', 
                                header=write_header, 
                                index=False)
                print(f"Found {len(successes)} successful prompts")

            check_for_success(0)

            # 4. Run BO optimization
            print(Fore.RED + "TEST: RUNNING BO OPTIMIZATION")
            new_prompts = bo.run_optimization_cycle(
                responses_path="responses.csv",
                prompts_dev_path="prompts-dev.csv"
            )

            # print(Fore.RED + "TEST: NEW PROMPTS" + new_prompts)
            print(Fore.RED + "TEST: NEW PROMPTS")

            print(Fore.RED + "TEST: UPDATING PROMPTS-DEV")
            # 5. Update prompts-dev.csv

            # THIS NEEDS TO BE CHECKED
            print(new_prompts)
            if new_prompts:
                with open("prompts-dev.csv", "a", newline='') as f:
                    writer = csv.writer(f)
                    for prompt, category in new_prompts:
                        writer.writerow([category, prompt, "BO", "no", ""])
                print(f"Added {len(new_prompts)} BO-optimized prompts")

            # 6. Check termination (3+ successes)
            # success_count = 0

            # check_for_success(0) Dont think i need this

            """
            if os.path.exists("success_db.csv"):
                try:
                    # Read CSV and handle headers if they exist
                    success_df = pd.read_csv("success_db.csv")
                    
                    # If no headers exist, the score will be in the last column
                    if 'score' not in success_df.columns:
                        success_df.columns = ['prompt', 'response', 'score'][:len(success_df.columns)]
                    
                    # Convert scores to numeric, forcing invalid values to NaN
                    success_df['score'] = pd.to_numeric(success_df['score'], errors='coerce')
                    
                    # Count only valid scores >= 8 (drops NaN values)
                    success_count = len(success_df[success_df['score'] >= 8].dropna())
                except Exception as e:
                    print(f"Error reading success file: {e}")
                    success_count = 0
            else:
                success_count = 0
            
            if success_count >= 3:
                print("\n=== TERMINATING - 3+ SUCCESSES FOUND ===")
                break
            """

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()
    

if __name__ == "__main__":
    main()
# ========================================