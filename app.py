from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, render_template, request, jsonify
import openai

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENROUTER_API_BASE", "https://api.openai.com/v1")
MODEL = "google/gemma-3n-e2b-it:free"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/generate", methods=["POST"])
def generate_script():
    data = request.get_json() or {}
    items = data.get("items", [])
    requirements = data.get("requirements", [])

    # Merge textarea items + uploaded list into one sequence
    combined = items + requirements

    # Build prompt
    prompt = f"""
Generate an idempotent Bash script for Ubuntu server that does the following:

1. Updates apt (only if not up to date) and installs missing apt packages.
2. Pulls Docker images and installs any packages.

Requested items:
{', '.join(combined)}

Each step must check for existing installation or running container before proceeding. Please do not include any explanation at the bottom.
"""

    response = openai.ChatCompletion.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=800
    )

    script = response.choices[0].message.content.strip()
    return jsonify({"script": script})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
