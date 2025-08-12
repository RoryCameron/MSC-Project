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
def display_results(csv_path, cycle, max_rows=100):
    
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

            print(Fore.GREEN + f"\n{'-' * 30}" +  f" Successful Injection #{idx} " + f"{'-' * 30}")

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

        #print(Fore.BLUE + "\n" + ("=" * 100))

        # display_graph("prompts-dev.csv") # Needs cleaned up first


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
    print(Fore.MAGENTA + "+ " + Fore.WHITE + "Prompt Injection Success Rate: {:.2f}%".format((successCount / totalCount) * 100) + Fore.MAGENTA + " +")
    print(Fore.MAGENTA + "+ " + Fore.WHITE +  "Query Efficiency: {}".format(totalCount) + Fore.MAGENTA + "                 +") # maybe minus seed prompts here?
    print(Fore.MAGENTA + "+ " + Fore.WHITE +  "Number of cycles: {}".format(cycle) + Fore.MAGENTA + "                 +")
    print(Fore.MAGENTA + ("=" * 40))

    print(Fore.BLUE + "\n" + ("=" * 100))
# ==========================================================



# ============ Display all prompt scores ============
def display_graph(csv_path):
    df = pd.read_csv(csv_path)

    df['tested'] = df['tested'].astype(str).str.lower().isin(['true', '1', 'yes'])

    df['score'] = pd.to_numeric(df['score'], errors='coerce')

    print("\n--- Distribution of Scores ---")
    total_prompts = len(df)
    scores = df['score'].dropna()
    scores = scores[(scores >= 1) & (scores <= 10)]

    if len(scores) > 0:
        freq = scores.round().astype(int).value_counts().reindex(range(1, 11), fill_value=0).sort_index()
        
        x = list(freq.index)
        y = list(freq.values)

        plt.clt()
        plt.bar(x, y)
        plt.title("Score Distribution (1 to 10)")
        plt.xlabel("Score")
        plt.ylabel("Prompt Count")
        plt.xticks(range(1, 11))
        plt.yticks(range(0, total_prompts + 1))
        plt.xlim(0.5, 10.5)
        plt.ylim(0, total_prompts)
        plt.show()
    else:
        print("No score data to display.")
# ===================================================


"""
if __name__ == "__main__":
    display_results("success_db.csv", 37)
    # display_graph("prompts-dev.csv")
"""