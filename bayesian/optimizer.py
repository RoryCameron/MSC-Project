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

from typing import List, Tuple

from bayesian.mutator import mutate_prompt_with_llm

from colorama import init, Fore, Style
import ast
# =================================



class BayesianOptimizer:
    def __init__(self):
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.model = None
        self.kernel = RBF(
            length_scale=1.0,
            length_scale_bounds=(1e-5, 1e5)  # Adjusted bounds
        ) + WhiteKernel(
            noise_level=1.0,
            noise_level_bounds=(1e-5, 1e5)   # Adjusted bounds
        )


    def train(self, prompts_dev_path: str) -> bool:
        
        # print(Fore.RED + "TEST: BO TRAINING FUNCTION")
        try:
            df = pd.read_csv(prompts_dev_path)
            tested = df[(df['tested'] == 'yes') & (df['score'].notna())]
            
            if len(tested) < 5: # Means always tested
                return False
                
            X = self.embedder.encode(tested['prompt'].tolist())
            y = tested['score'].astype(float).values
            self.model = GaussianProcessRegressor(kernel=self.kernel).fit(X, y)
            # print(Fore.RED + "TEST: END OF BO TRAINING FUNCTION")
            return True
        except Exception as e:
            print(f"[BO Training Error] {e}")
            return False


    def run_optimization_cycle(self, responses_path: str, prompts_dev_path: str) -> List[Tuple[str, str]]:

        # print(Fore.RED + "TEST: BO OPTIMIZATION CYCLE")

        # 1. Load medium-scoring prompts (5-7)
        df = pd.read_csv(responses_path)

        df['score'] = pd.to_numeric(df['score'], errors='coerce')
        df = df.dropna(subset=['score'])

        candidates = df[(df['score'] >= 1) & (df['score'] < 8)] # Change this for what range of prompts are mutated
        
        # 2. Call mutator.py for each candidate
        mutations = []
        for _, row in candidates.iterrows():
            # ===== MUTATOR.PY CALL =====
            mutated = mutate_prompt_with_llm(
                row['prompt'],
                row['response'],
                row['score']
            )
            
            # print(Fore.BLUE + "DEBUG: MUTATED")
            # print(mutated)
            # print(Fore.RED + "TEST: MUTATED PROMPTS IN OPTIMIZER " + mutated)
            
            if isinstance(mutated, str):
                try:
                    # Try parsing first in case it's a clean list string
                    parsed = ast.literal_eval(mutated)
                    if isinstance(parsed, list):
                        mutated = parsed
                    else:
                        # fallback: split manually by triple quotes or newlines
                        mutated = [
                            p.strip()
                            for p in mutated.split('"""')
                            if p.strip()
                        ]
                except Exception as e:
                    print(f"Failed to parse mutated string: {e}")
                    mutated = [
                        p.strip()
                        for p in mutated.split('"""')
                        if p.strip()
                    ]

            valid_mutations = [
                (str(m).strip(), str(row['category']).strip())
                for m in mutated
                if m and str(m).strip()
            ]
            
            # 2. Validate before extending
            if valid_mutations:
                print(f"Adding {len(valid_mutations)} valid mutations")
                mutations.extend(valid_mutations)
            else:
                print(f"All mutations filtered out from: {mutated}")

            # print(mutations)

        # 3. Bayesian Selection
        if self.train(prompts_dev_path) and mutations:
            prompts = [m[0] for m in mutations]
            selected = self.select_best(prompts)
            return [(p, cat) for p, (_, cat) in zip(selected, mutations) if p in selected]
        return []

    def select_best(self, prompts: List[str]) -> List[str]:

        #print(Fore.RED + "TEST: BO SELECT BEST")

        # if model not trained yet
        """
        if not self.model:
            return prompts[:3]
        """
        
        # Select top candidates using UCB 
        X = self.embedder.encode(prompts)
        means, stds = self.model.predict(X, return_std=True)
        return [prompts[i] for i in np.argsort(means + 2.0 * stds)[-5:]] # Change using CLI arg - selects top  prompts