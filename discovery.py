"""
File: discovery.py
Author: Rory Cameron
Date: 23/06/2025
Description: Automates discovery of chatbot selectors
"""


# ============ Imports ============
import time
import json
import os
from dotenv import load_dotenv

import openai
# =================================


# ============ Load environment variables ============
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment")
# ====================================================



# ============ Initialize OpenAI client ============
client = openai.OpenAI(api_key=api_key)
# ==================================================



# ============ Functions ============

def extract_json_from_text(text):
    start = text.find('{')
    end = text.rfind('}')
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in GPT output")
    json_str = text[start:end+1].strip('` \n')
    return json.loads(json_str)


def discover_selectors(driver, url):
    """
    Loads the url using provided Selenium driver,
    then uses GPT to analyze the DOM and extract chatbot selectors.
    
    Returns a dict with 'input_selector', 'send_selector', 'response_selector'.
    """
    driver.get(url)
    time.sleep(5)  # wait for page load/render

    dom = driver.page_source

    print("Analyzing DOM with GPT to find chatbot selectors...")
    prompt = f"""
You're a security tester analyzing the DOM of a webpage. 
From the given DOM, extract a JSON object specifying:

- input_selector: CSS selector string for the chatbot user input field.
- send_selector: CSS selector string for the chatbot send button.
- response_selector: CSS selector string for the container holding chatbot responses.

DOM snapshot:
{dom[:8000]}
"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful web automation expert."},
            {"role": "user", "content": prompt}
        ]
    )
    
    raw = response.choices[0].message.content
    print("Raw GPT output:\n", raw)
    
    selectors = extract_json_from_text(raw)
    print("Extracted selectors:", selectors)
    return selectors
# ===================================
