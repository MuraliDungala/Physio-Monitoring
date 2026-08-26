#!/usr/bin/env python
"""
Start the Physio Monitoring backend server
"""
import sys
import os
import subprocess
from pathlib import Path

if sys.platform == 'win32' and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

env = os.environ.copy()
env["PYTHONUTF8"] = "1"
env["PYTHONIOENCODING"] = "utf-8"

backend_dir = Path(__file__).resolve().parent
os.chdir(str(backend_dir))
sys.path.insert(0, str(backend_dir))

print(f"🚀 Starting Physio Monitoring Backend...")
print(f"📁 Backend Dir: {backend_dir}")
print(f"🐍 Python Executable: {sys.executable}")
print(f"🌐 Server URL: http://localhost:8000")
print("=" * 60)

subprocess.run([
    sys.executable, "-m", "uvicorn",
    "app:app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--reload"
], cwd=str(backend_dir), env=env)
