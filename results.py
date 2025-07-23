"""
File: results.py
Author: Rory Cameron
Date: 23/07/2025
Description: Generating and formatting results to be displayed to user
"""



# ============ Imports ============
import sys
import os
import csv
import pyfiglet
from colorama import init, Fore, Style
# =================================



init(autoreset=True)



# Implement way to show prompts-dev to show scores of all prompts, succesful or not
def display_results(csv_path, max_rows=100):
    
    if not os.path.exists(csv_path):
        print(Fore.RED + f"File not found: {csv_path}")
        print(Fore.RED + "No Successful Results")
        return

    print(Fore.BLUE + "\n" + ("=" * 100))

    ascii_art = pyfiglet.figlet_format("Results", font="slant")
    print(ascii_art)

    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for idx, row in enumerate(reader, 1):
            if idx > max_rows:
                print(Fore.WHITE + f"\n...showing first {max_rows} rows.")
                break

            print(Fore.MAGENTA + f"\n{'-' * 30}" +  f" Injection #{idx} " + f"{'-' * 30}")

            """
            print(Fore.YELLOW + Style.BRIGHT + "Category:")
            print(row["category"])
            """

            print(Fore.YELLOW + Style.BRIGHT + "\nPrompt:")
            print(row["prompt"])

            print(Fore.YELLOW + Style.BRIGHT + "\nResponse:")
            print(row["response"])

            # Score color
            try:
                score_val = float(row["score"])
                if score_val >= 8:
                    score_color = Fore.RED + Style.BRIGHT
                elif score_val >= 5:
                    score_color = Fore.YELLOW
                else:
                    score_color = Fore.GREEN
            except ValueError:
                score_color = Fore.WHITE

            print(Fore.YELLOW + Style.BRIGHT + "\nScore:")
            print(score_color + row["score"])

            print(Fore.YELLOW + Style.BRIGHT + "\nLLM Explanation:")
            print(row["explanation"])

        print(Fore.BLUE + "\n" + ("=" * 100))

"""
if __name__ == "__main__":
    display_injections("success_db.csv")
"""