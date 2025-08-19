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
    driver.get(url)
    time.sleep(5)  # wait for page load/render

    dom = driver.page_source

    print("Analyzing DOM with GPT to find chatbot selectors...")
    prompt = f"""
You're a security tester analyzing the DOM of a webpage.
Your goal is to extract selectors for a chatbot
From the given DOM, extract a JSON object specifying:

- input_selector: CSS selector string for the chatbot user input field.
- send_selector: CSS selector string for the chatbot send button.
- response_selector: CSS selector string for the container holding chatbot responses.
- bot_response_selector: CSS selector string for the individual bot responses, not the full chat container. This should correspond to a single message sent by the chatbot.
- toggle_selector: CSS selector for chat toggle button.
- toggle_state: String either "open" or "closed". "open" if the chatbot is initially visible/accessible on the target website, and no button has to be clicked to access it. "closed" if the chatbot is not initially visible/accessible on the target website, and a button has to be clicked to access it.

Rules:
- Only include toggle_selector and toggle_state if you find a button that expands/hides the chatbot.
- If chat is always visible with no toggle button, omit toggle_selector and toggle_state entirely.
- Ignore all everything unrelated to the chatbhot, such as UI elements such as site search bars, newsletter signups, forms, or non chat-bot inputs.
- Ignore search bars, newsletter fields, login forms, and anything outside the chatbot.
- No guessing generic names like .response-container, .bot-response, .chat-toggle unless they actually exist in the DOM
- DO NOT MAKE UP CHATBOT SELECTORS, THEY MUST BE EXACT AND EXIST IN THE DOM. DO NOT GET DISTRACTED BY OTHER PARTS OF THE PAGE, LOOK FOR THINGS DIRECTLY RELATING TO A CHATBOT
- Scope check: For input, send, and response selectors, only choose elements inside the chatbot container. Ignore unrelated inputs/buttons anywhere else on the page.

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
    # print("Raw GPT output:\n", raw)
    
    selectors = extract_json_from_text(raw)
    # print("Extracted selectors:", selectors)
    return selectors
# ===================================
