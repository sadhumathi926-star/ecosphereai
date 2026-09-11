"""
app.py

Flask backend for EcoSphere AI. It exposes:
- GET  /        -> renders the chat UI (templates/index.html)
- POST /chat    -> receives a user message, sends it to the Gemini API
                   together with the system prompt, and returns the
                   model's reply as JSON.
"""

import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types

from chatbot_config import SYSTEM_PROMPT

# Load environment variables from .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-3.1-flash-lite"

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. Please add it to your .env file."
    )

# Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

app = Flask(__name__)


@app.route("/")
def index():
    """Render the chat interface."""
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """Receive a user message and return EcoSphere AI's reply."""
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
            ),
        )
        reply = response.text or "Sorry, I couldn't generate a response."
        return jsonify({"reply": reply})

    except Exception as exc:  # noqa: BLE001
        app.logger.error("Gemini API error: %s", exc)
        return jsonify({"error": "Something went wrong. Please try again."}), 500


if __name__ == "__main__":
    app.run(debug=True)
