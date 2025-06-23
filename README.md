# Automated Black-Box Prompt Injection on Web-Embedded Chatbots via Bayesian Optimization

## Problem Statement
With the continual growth and development of Large Language Models (LLM’s), Chatbot technology has significantly improved, with ever increasing adoption by companies into their own websites with 55% of companies planning to add a chatbot to improve their customer service interactions (Fokina, 2024). Whilst these chatbots can provide significant benefits to a company, including increased user engagement, faster customer support and overall operational automation, they are also susceptible to the emerging vulnerability of prompt injection. Ranked as the top vulnerability in OWASP’s Top 10 for Generative AI and LLM’s, Prompt Injection occurs when adversaries embed malicious instructions within prompts. This can manipulate a chatbots behaviour, leading to unintended or harmful outputs (OWASP, 2024).

Prompt injection is an emerging and critical vulnerability that, despite increasing awareness, remains largely underexplored in academic research and is often not addressed in commercial deployments. Existing studies:

- Propose an automated black box framework utilising iterative prompt refinement via a LLM in a feedback loop, resulting in heavy prompt usage on the target, increasing the likelihood of detection and hitting defensive limits (Liu et al., 2024).
- Propose an automated framework with gradient-based prompt generation, however solely focuses on indirect injection, not applicable to many web-embedded chatbots (Liu et al., 2024).
- Proposes injection technique for effective defence evasion, however this technique also relies on indirect injection and manual prompt input/crafting (Greshake et al., 2023).

Existing literature shows a clear gap in the failure to combine full automation from the discovery stage with stealthy prompt generation and testing, which without could render frameworks impractical when faced with rate-limits and other defensive measures.

## Project Aim
The aim of this project is to develop an automated framework for conducting stealthy direct prompt injection attacks against black-box, web-embedded LLM-based chatbots. The framework will utilize a large language model (LLM) in the discovery phase to identify interaction points and generate malicious prompts, guided by Bayesian Optimization.

## Research Questions
- RQ1: How can Bayesian Optimization guide LLM-generated prompt selection to enable efficient and automated direct prompt injection in black-box environments?
- RQ2: To what extent can the proposed framework perform effective prompt injection while minimizing prompt volume and avoiding detection or rate-limiting mechanisms?
- RQ3: How well does the proposed framework generalize across different Black-Box LLM’s and web-embedded chatbots?

## Project Objectives
1. Design and develop an automated discovery module that utilizes an LLM to identify user input fields and capture chatbot responses.
2. Design and develop a prompt generation module that uses an LLM to craft direct prompt injection attacks.
3. Apply Bayesian Optimization to guide the selection and refinement of prompts, aiming to maximize effectiveness while minimizing the number of prompts sent.
4. Evaluate the proposed framework’s effectiveness and generalizability across multiple black-box LLM chatbot environments and compare the performance of Bayesian Optimization with other machine learning algorithms from existing literature.
5. Explore the ethical considerations of an automated prompt injection framework, with particular attention to its dual-use potential for both defensive and adversarial applications.

## Feasibility, Significance and Potential for Innovation
he feasibility of this project is supported by the availability of numerous resources relevant to its scope. Various LLM APIs, such as OpenAI, LLaMA and Gemini provide solid platforms for implementing the framework and creating test environments. Additionally, publicly available datasets on Kaggle such as *prompt-injection-in-the-wild* and *prompt-injection-paraphrase-attack* offer prompt injection examples for model training. Finally, Python libraries such as *scikit-optimize*, allow for the easy integration of Bayesian Optimization into the framework. 

The significance of this project lies in its focus on the critical and emerging vulnerability of prompt injection in LLM web-embedded chatbots. As these systems grow in popularity so to do the associated risks and potential threats. Existing literature reveals a general lack of awareness regarding the need for robust protective measures. By developing an automated and stealthy prompt injection framework, this research aims to provide companies with valuable insights, improving their AI security posture.

The proposed approach is innovative in its combination of automated discovery and prompt generation, guided by Bayesian Optimization. Unlike existing work, which often depends on manually crafted prompts and indirect injection techniques, this framework targets direct injection while minimizing prompt volume. The use of Bayesian Optimization reduces reliance on prompt-heavy refinement loops, making the approach less query intensive and less detectable. Additionally, the framework is designed to operate in a black-box setting, requiring no prior knowledge of the chatbot’s internal structure, better simulating realistic attack scenarios. Finally, the inclusion of ethical guidelines will help ensure that the framework is applied responsibly, with a focus on improving defences rather than enabling malicious use.