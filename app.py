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
You are an expert at Ubuntu Server
Generate a Bash script for Ubuntu server that does the following requested actions:
{', '.join(combined)}
The script will be run in a privilaged docker container (so do not use sudo) and its output will be saved so make sure the output is formatted well. Make sure that anything that must be tested or verified clearly indicates a pass or fail.
The script should be robust and self-contained. Do not include any explanatory text, markdown formatting, or anything other than the raw script code itself.
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
