#!/usr/bin/env python
"""
Start the Physio Monitoring backend server
"""
import sys
import os
import subprocess

# Change to backend directory
backend_dir = os.path.join(os.path.dirname(__file__), "physio-web", "backend")
os.chdir(backend_dir)

# Add backend to path
sys.path.insert(0, backend_dir)

print(f"Starting server from: {os.getcwd()}")
print(f"Python: {sys.executable}")
print("=" * 60)

# Run uvicorn
subprocess.run([
    sys.executable, "-m", "uvicorn",
    "app:app",
    "--host", "0.0.0.0",
    "--port", "8000",
    "--reload"
], cwd=backend_dir)
