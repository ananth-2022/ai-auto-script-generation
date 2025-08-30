from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, render_template, request, jsonify
import openai

import subprocess
import datetime
from flask import flash, redirect, url_for, render_template
from werkzeug.utils import secure_filename


app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.api_base = os.getenv("OPENROUTER_API_BASE", "https://api.openai.com/v1")
MODEL = "google/gemini-2.5-flash-image-preview:free"

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
The script will be run in a privilaged docker container (so do not use sudo) and its output will be saved so make sure the output is formatted well. Make sure that anything that must be tested or verified clearly indicates a pass or fail. Perform any requested tests or verification only after installing all packages.
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

# -----------------------------------------------------------------------------
# BEGIN: Docker‐run support (do not modify existing functions above)
# -----------------------------------------------------------------------------

# Configuration for upload + Docker
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTS  = {"sh"}
IMAGE_NAME    = "bash-web-tester"
LOG_FILENAME  = "last_run.log"

# Ensure upload dir exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTS
    )


def build_image():
    """(Re)builds the Docker image used to run every script."""
    subprocess.run(
        ["docker", "build", "-t", IMAGE_NAME, "."],
        check=True
    )


def run_in_container(script_filename):
    """
    Runs the given script (from uploads/) in a throwaway container.
    Returns a CompletedProcess with stdout/stderr/returncode.
    """
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{os.path.abspath(UPLOAD_FOLDER)}:/app",
        IMAGE_NAME,
        "bash", f"/app/{script_filename}"
    ]
    return subprocess.run(cmd, capture_output=True, text=True)


def format_log(script_name, proc):
    """Builds the timestamped log text."""
    now = datetime.datetime.now().isoformat()
    parts = [
        f"Script:     {script_name}",
        f"Run at:     {now}",
        f"Exit code:  {proc.returncode}",
        "",
        "----- STDOUT -----",
        proc.stdout or "<no stdout>",
        "",
        "----- STDERR -----",
        proc.stderr or "<no stderr>",
    ]
    return "\n".join(parts)


@app.route("/run", methods=["POST"])
def run_script():
    """
    Accepts either:
      1) file upload named "script_file"
      2) raw script text named "script"
    Saves to uploads/, builds the image, runs the script, and renders result.html.
    """
    upload = request.files.get("script_file")
    script_text = request.form.get("script", "").strip()
    script_text = script_text.replace("\r\n", "\n").replace("\r", "")

    # Decide where the script comes from
    if upload and upload.filename:
        filename = secure_filename(upload.filename)
        if not allowed_file(filename):
            flash("Only .sh files are allowed.")
            return redirect(url_for("index"))
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        upload.save(filepath)

    elif script_text:
        # save AI‐generated script
        filename = f"generated_{int(datetime.datetime.now().timestamp())}.sh"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, "w") as f:
            f.write(script_text + "\n")

    else:
        flash("No script provided.")
        return redirect(url_for("index"))

    # ensure executable
    os.chmod(filepath, 0o755)

    # (Re)build image
    try:
        build_image()
    except subprocess.CalledProcessError:
        flash("Failed to build Docker image.")
        return redirect(url_for("index"))

    # run it
    proc = run_in_container(filename)
    logtext = format_log(filename, proc)

    # persist last run
    with open(LOG_FILENAME, "w") as f:
        f.write(logtext)

    return render_template("result.html", log=logtext)
# -----------------------------------------------------------------------------
# END: Docker‐run support
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True, port=5000)
