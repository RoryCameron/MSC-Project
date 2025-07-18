"""
File: promptInjector.py
Author: Rory Cameron
Date: 30/06/2025
Description: Bayesian optimization module
"""



# ============ Imports ============
import pandas as pd
import numpy as np

from sentence_transformers import SentenceTransformer

from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel

import csv
# =================================



# ============ Config ============
PROMPT_FILE = "prompts.dev.csv" #Harcoded change later to be passed in function
TOP_K = 10  # Number of new prompts to suggest
MODEL_NAME = "all-MiniLM-L6-v2"
# =================================



def load_prompts():
    df = pd.read_csv(PROMPT_FILE)
    df["prompt"] = df["prompt"].astype(str)
    return df



def get_embeddings(prompts, model):
    return model.encode(prompts, show_progress_bar=False)



def train_bo_model(X, y):
    kernel = RBF(length_scale=1.0) + WhiteKernel(noise_level=1)

    model = GaussianProcessRegressor(kernel=kernel, alpha=1e-6, normalize_y=True)
    model.fit(X,y)
    return model



def acquisition_ucb(mean, std, beta=2.0):
    return mean + beta + std



def select_canditates(df, model, embedder, top_k=TOP_K):
    untested = df[df["tested"].str.lower() == "no"].copy()

    if untested.empty:
        print("No untested prompts left")
        return []

    X_unseen = get_embeddings(untested["prompt"].tolist(), embedder)
    mean, std = model.predict(X_unseen, return_std=True)
    scores = acquisition_ucb(mean, std)

    untested["acquisition_score"] = scores
    top = untested.sort_values("acquisition_score", ascending=False).head(top_k)
    return top[["prompt", "category"]].values.tolist()



def append_new_prompts(candidates):
    with open(PROMPT_FILE, mode="a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for prompt, category in candidates:
            writer.writerow([category, prompt, "bo", "no"])
    print(f"[+] Appended {len(candidates)} BO-generated prompts to {PROMPT_FILE}")
