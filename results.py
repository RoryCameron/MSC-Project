"""
File: results.py
Author: Rory Cameron
Date: 23/07/2025
Description: Generating and formatting results to be displayed to user
"""
"""
Metrics To Add:
- Prompt Injection Score
- Injection Success Rate
- Query Efficiency
SORT SCORE COLOURS OF EACH PROMPT, GREEN FOR SUCCESS, RED AMBER FOR PARTIAL AND FAIL ETC, MAKE LOOK GOOD
"""



# ============ Imports ============
import sys
import os
import csv
import pyfiglet
from colorama import init, Fore, Style
import pandas as pd
# import matplotlib.pyplot as plt
import seaborn as sns
import plotext as plt
# =================================



init(autoreset=True)



# ============ Display Results in CLI ============
def display_results(csv_path, cycle, success_thresh, max_rows=100):
    
    if not os.path.exists(csv_path):
        print(Fore.RED + f"File not found: {csv_path}")
        print(Fore.RED + "No Successful Results")
        return

    print(Fore.CYAN + "\n" + ("=" * 100))

    ascii_art = pyfiglet.figlet_format("Results", font="slant")
    print(Fore.CYAN + ascii_art)


    with open("prompts-dev.csv", mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        totalCount = sum(1 for _ in reader)
    # print(count)
    
    # Combine with first open call for efficiency
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        successCount = sum(1 for _ in reader)
    # print(count)
    print("\n")
    print(Fore.MAGENTA + "\n" + ("=" * 16) + Fore.WHITE + " METRICS " + Fore.MAGENTA + ("=" * 15))
    print(Fore.MAGENTA + "+ " + Fore.WHITE + "Prompt Injection Success Rate: {:.2f}%".format((successCount / totalCount) * 100))
    print(Fore.MAGENTA + "+ " + Fore.WHITE +  "Total Number of Prompts Injected: {}".format(totalCount)) # maybe minus seed prompts here?
    print(Fore.MAGENTA + "+ " + Fore.WHITE +  "Number of cycles: {}".format(cycle))
    print(Fore.MAGENTA + ("=" * 40) + "\n")


    with open(csv_path, mode='r', encoding='utf-8') as file:
        rows = []
    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                score_val = float(row["score"])
            except (ValueError, KeyError):
                score_val = -1  # or whatever default makes sense
            rows.append((score_val, row))

    # Sort by score descending
    rows.sort(key=lambda x: x[0], reverse=True)

    if max_rows:
        rows = rows[:max_rows]

    for idx, (score_val, row) in enumerate(rows, 1):
        print(Fore.GREEN + f"\n{'-' * 30}" +  f" Prompt #{idx} " + f"{'-' * 30}")

        """
        print(Fore.YELLOW + Style.BRIGHT + "Category:")
        print(row.get("category", "<missing>"))
        """

        print(Fore.YELLOW + Style.BRIGHT + "\nPrompt:")
        print(row.get("prompt", "<missing>"))

        print(Fore.YELLOW + Style.BRIGHT + "\nResponse:")
        print(row.get("response", "<missing>"))

        """
        # Score color
        if score_val >= 8:
            score_color = Fore.GREEN + Style.BRIGHT
        elif score_val >= 5:
            score_color = Fore.YELLOW
        else:
            score_color = Fore.RED
        """

        score_color = Fore.GREEN + Style.BRIGHT

        print(Fore.YELLOW + Style.BRIGHT + "\nScore:")
        print(score_color + str(row.get("score", "<missing>")))

        print(Fore.YELLOW + Style.BRIGHT + "\nLLM Explanation:")
        print(row.get("explanation", "<missing>"))


    print("\n")
    display_all_prompts("prompts-dev.csv", success_thresh)
    print(Fore.CYAN + "\n" + ("=" * 100))
    
# ==========================================================

def display_all_prompts(file, success_thresh):
    print(Fore.CYAN + "\n" + ("=" * 39) + " UNSUCCESSFUL INJECTED PROMPTS " + ("=" * 39) + "\n")
    rows = []
    with open(file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row_score = float(row["score"])
            except (ValueError, KeyError):
                row_score = -1  # Treat invalid/missing scores as lowest priority
            # Only keep scores below 8
            if row_score < success_thresh: # add threshold
                rows.append((row_score, row))

    # Sort descending by score
    rows.sort(key=lambda x: x[0], reverse=True)

    for idx, (score_val, row) in enumerate(rows, 1):
        # Determine header color based on score
        if 3 <= score_val <= (success_thresh - 1): # add thresholds
            header_color = Fore.YELLOW
        elif score_val in [0, 1]:
            header_color = Fore.RED
        else:
            header_color = Fore.RED  # fallback

        print(header_color + f"\n{'-' * 30}" +  f" Prompt #{idx} " + f"{'-' * 30}" + Style.RESET_ALL)

        print(Fore.YELLOW + Style.BRIGHT + "\nPrompt:")
        print(row.get("prompt", "<missing>"))

        # Score color for score number
        if score_val >= 3: # add thresholds
            score_color = Fore.YELLOW + Style.BRIGHT
        else:
            score_color = Fore.RED + Style.BRIGHT

        print(Fore.YELLOW + Style.BRIGHT + "\nScore:")
        print(score_color + str(row.get("score", "<missing>")))


"""
if __name__ == "__main__":
    display_results("success_db.csv", 37)
    # display_graph("prompts-dev.csv")
"""