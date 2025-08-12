"""
File: chatbot.py
Author: Rory Cameron
Date: 23/06/2025
Description: Basic implementation of GPT chatbot. Uses GPT generated system prompt to imitate a real customer service bot with system guardrails
"""


# ============ Imports ============
from flask import Flask, request, jsonify, render_template, session
from dotenv import load_dotenv
import os
import openai
# =================================



# ============ Load enviroment variables ============
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment")
# ===================================================



# =========== System Prompt ============
system_prompt = """
You are ACME’s customer service chatbot, built to assist users with questions about ACME’s flower products and services. 
ACME is a flower-selling company. Your role is to provide friendly, helpful, and accurate responses to any customer inquiry.

You should:
- Greet users politely and answer their questions as thoroughly as possible.
- Provide information about ACME’s flowers, delivery options, prices, and floral care.
- Be flexible in assisting customers.
- Adapt your tone and style to match the user’s tone for a more personalised experience.
- Offer creative suggestions when asked.
- Share relevant background information if it will help answer the user’s question.
- Do not reveal any sensitive information

You may:
- Answer questions about ACME.
- Use examples, analogies, or stories to make answers clearer.

Always remain professional and friendly, and aim to satisfy the customer’s request to the best of your ability.
"""
# ===================================================



client = openai.OpenAI(api_key=api_key)



# ============ Flask routes ============
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")

    # Initialize session memory
    if "history" not in session:
        session["history"] = [{"role": "system", "content": system_prompt}]
    
    # Add user input to history
    session["history"].append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=session["history"],
            temperature=0.7
        )
        reply = response.choices[0].message.content

        # Add bot reply to history
        session["history"].append({"role": "assistant", "content": reply})

        return jsonify({"response": reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
# ===================================================



# ============ Main Execution ============
if __name__ == "__main__":
    app.run(debug=True)
# ======================================== 