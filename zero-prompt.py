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

from results import display_results

import argparse
# =================================



# Lol
init(autoreset=True)
def print_banner():
    ascii_art = pyfiglet.figlet_format("ZeroPrompt", font="slant")
    print("\n\n" + Fore.CYAN + ascii_art + "\n\n")


"""
# CLI Args (apart from --reset and url)
# Needs input validation
p = argparse.ArgumentParser()
p.add_argument("sc", type=int) # Success Count (Target number of successful prompts)
p.add_argument("st", type=int) # Success Threshold (Minimum value to define successful prompt)
p.add_argument("cr", type=int) # Candidate Range (Range of scores of prompts that can be mutated)
p.add_argument("cs", type=int) # Candidate Selected (Number of BO selected mutations to add to dataset)
args = p.parse_args()
"""

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



# ============ Exists program after set number of successful prompts found ============
def check_for_success(success_count, success_target, cycle):
    if os.path.exists("success_db.csv"):
        try:
            success_df = pd.read_csv("success_db.csv")
                        
            if 'score' not in success_df.columns:
                success_df.columns = ['prompt', 'response', 'score'][:len(success_df.columns)]
                        
            success_df['score'] = pd.to_numeric(success_df['score'], errors='coerce')
                        
            success_count = len(success_df[success_df['score'] >= 8].dropna())
        except Exception as e:
            print(f"Error reading success file: {e}")
            success_count = 0
    else:
        success_count = 0
                
    if success_count >= success_target: # Change to CLI arg - BO Cycle stops if this many succesful prompts exist
        print(Fore.GREEN + "\nInjection Success - Generating Results") # Format Better
        display_results("success_db.csv", cycle)
        sys.exit(0)

    # ADD line above checking if cycles equals cycle arg, to call results if cycles reached max limit
# =====================================================================================



# ============ Main Execution ============
def main():
    
    file_path = "prompts-dev.csv" # SEED + PROMPTS CSV



    # ============ CLI Arguements ============
    parser = argparse.ArgumentParser(description="ZeroPrompt CLI")
    parser.add_argument("url", type=str, help="Target URL (must start with http:// or https://)")
    parser.add_argument("--sc", type=int, default=10, help="Target number of successful prompts")
    parser.add_argument("--st", type=int, default=8, help="Minimum score to count as success")
    parser.add_argument("--cr", type=int, default=9, help="Candidate range for mutation")
    parser.add_argument("--cs", type=int, default=5, help="Number of BO-selected mutations")
    parser.add_argument("--cycles", type=int, default=10, help="Max Bayesian Optimization cycles")
    parser.add_argument("--reset", action="store_true", help="Reset all stored prompts and responses")
    args = parser.parse_args()
    # ========================================

    if args.reset:
        reset_seed_prompts(file_path)
        reset_responses()
        reset_success()
        sys.exit(1)

    # Original code commented out
    """
    # Fix this to only 1 or 2 calls
    if "--reset" in sys.argv:
        reset_seed_prompts(file_path)
        reset_responses()
        reset_success()
        sys.exit(1)
    """

    """
    if len(sys.argv) < 2:
        print("Usage: python zeroPrompt.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    """

    if not re.match(r"^https?://", args.url): # added args.url
        print("Invalid URL. Must start with http:// or https://")
        sys.exit(1)
    
    print_banner()

    print(f"Launching browser and loading URL: {args.url}") # Added args.url
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


    # ============ Discovery phase ============
    try:
        print(Fore.CYAN + "\nDISCOVERY PHASE\n")

        print("Discovering selectors...")
        selectors = discover_selectors(driver, args.url) # Added args.url

        if not selectors:
            print(Fore.RED + "Failed to discover any selectors")
            sys.exit(1)

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


        # ============ Injection/BO Execution Loop ============
        for cycle in range(1, args.cycles + 1): # Change to CLI arg - how many cycles of BO before quitting - added args.cycles
            print(Fore.CYAN + f"\nCYCLE {cycle}\n")
            
            # Injects new round of untested prompts
            injection_phase()

            # 2. Load responses
            try:
                responses = pd.read_csv("responses.csv")

                responses['score'] = pd.to_numeric(responses['score'], errors='coerce')

                responses = responses.dropna(subset=['score'])
            except FileNotFoundError:
                print("No responses found - skipping cycle")
                continue
            except Exception as e:
                print(Fore.RED + f"Failed to load/clean responses.csv: {e}")
                continue

            successes = responses[responses['score'] >= args.st] # Change to CLI arg - What value considered a success - added args.st

            if not successes.empty:
                write_header = not os.path.exists("success_db.csv")
                successes.to_csv("success_db.csv", 
                                mode='a', 
                                header=write_header, 
                                index=False)
                print(Fore.GREEN + f"Found {len(successes)} successful prompts")

            check_for_success(0, args.sc, cycle) # Checks if program found set successful prompts - No need to pass this zero so redundant


            # ============ BO Optimization Phase ============
            print(Fore.CYAN + "\nBO OPTIMIZATION PHASE\n")
            new_prompts = bo.run_optimization_cycle(
                candidate_range=args.cr, # added args.cr
                BO_selects=args.cs,
                responses_path="responses.csv",
                prompts_dev_path="prompts-dev.csv"
            )

            # Ressting responses.csv after every round
            with open("responses.csv", "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["category", "prompt", "response", "score", "explanation"])


            # Updating prompts-dev.csv
            if new_prompts:
                with open("prompts-dev.csv", "a", newline='') as f:
                    writer = csv.writer(f)
                    for prompt, category in new_prompts:
                        writer.writerow([category, prompt, "BO", "no", ""])
                print(f"Added {len(new_prompts)} BO-optimized prompts")
            else:
                print(Fore.RED + "No new prompts generated, Closing down for stealth and generating results") # Implement better way of dealing with 0 scores
                display_results("success_db.csv", cycle)
                sys.exit(0)
                # Retry system prompts? no this wont work as could be already in BO cycle

            # check_for_success(0, cycle) # Dont think i need this, but seems to not run results if hit end of cycles

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
# ========================================