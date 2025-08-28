import os
import subprocess
import datetime

# 1. Docker image name
IMAGE_NAME = "bash-single-test"

# 2. Set this to the bash script you want to run
SCRIPT_TO_RUN = "test_script.sh"

# 3. Output log filename (on the host)
OUTPUT_LOG = "test_results.txt"

def build_image():
    """Builds the Docker image from the Dockerfile in this folder."""
    subprocess.run(
        ["docker", "build", "-t", IMAGE_NAME, "."],
        check=True
    )

def run_in_container():
    """
    Runs the specified bash script inside a temporary container.
    --rm ensures the container is deleted after exit.
    """
    cmd = [
        "docker", "run",
        "--rm",
        "-v", f"{os.getcwd()}:/app",      # mount current dir to /app
        IMAGE_NAME,                       # the image to use
        "bash", f"/app/{SCRIPT_TO_RUN}"   # command to run
    ]
    return subprocess.run(cmd, capture_output=True, text=True)

def save_output(proc):
    """Writes timestamp, exit code, stdout and stderr to OUTPUT_LOG."""
    with open(OUTPUT_LOG, "w") as f:
        now = datetime.datetime.now().isoformat()
        f.write(f"Script:     {SCRIPT_TO_RUN}\n")
        f.write(f"Run at:     {now}\n")
        f.write(f"Exit code:  {proc.returncode}\n\n")
        f.write("----- STDOUT -----\n")
        f.write(proc.stdout or "<no stdout>\n")
        f.write("\n----- STDERR -----\n")
        f.write(proc.stderr or "<no stderr>\n")

def main():
    if not os.path.isfile(SCRIPT_TO_RUN):
        print(f"Error: '{SCRIPT_TO_RUN}' not found in current directory.")
        return

    print("Building Docker image...")
    build_image()

    print(f"Running '{SCRIPT_TO_RUN}' inside container (will auto-delete)...")
    proc = run_in_container()

    print("Saving logs to", OUTPUT_LOG)
    save_output(proc)

    print("✅ Done. Container was removed (--rm flag).")

if __name__ == "__main__":
    main()
