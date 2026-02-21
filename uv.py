import subprocess
import sys
import os

VENV_DIR = "venv"
REQUIREMENTS = "requirements.txt"

if not os.path.exists(VENV_DIR):
    print("Creating Python virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", VENV_DIR])

if sys.platform == "win32":
    python_bin = os.path.join(VENV_DIR, "Scripts", "python.exe")
else:
    python_bin = os.path.join(VENV_DIR, "bin", "python")

if not os.path.exists(REQUIREMENTS):
    print(f"{REQUIREMENTS} not found. Exiting.")
    sys.exit(1)
print("Installing dependencies...")
subprocess.run([python_bin, "-m", "pip", "install", "--upgrade", "pip"])
subprocess.run([python_bin, "-m", "pip", "install", "-r", REQUIREMENTS])

print("Launching Streamlit app...")
subprocess.run([python_bin, "-m", "streamlit", "run", "app.py"])
