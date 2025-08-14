"""
File: confusion_matrix.py
Author: Rory Cameron
Date: 14/08/2025
Description: Generate confusion matrixes for scorer LLM system prompts
"""


import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def confusionMatrix(num,TP,FP,TN,FN):

    conf_matrix = np.array([[TN, FP],
                        [FN, TP]])

    labels = np.array([["{}\n(TN)".format(TN), "{}\n(FP)".format(FP)],
                    ["{}\nFN".format(FN), "{}\nTP".format(TP)]])


    # Plot
    sns.heatmap(conf_matrix, annot=labels, fmt="", cmap="Blues")
    plt.title("Scorer LLM System Prompt {}\n".format(num))
    plt.xlabel("Predicted")
    plt.ylabel("Actual")
    plt.show()

confusionMatrix(1, 7,0,11,13)
confusionMatrix(2, 3,0,10,18)
confusionMatrix(3, 11,0,5,15)
confusionMatrix(4, 13,0,7,11)
