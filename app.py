import sys
import os
from pathlib import Path

# Add physio-web/backend to sys.path so app module and dependencies resolve
backend_dir = Path(__file__).resolve().parent / "physio-web" / "backend"
if backend_dir.exists():
    os.chdir(str(backend_dir))
    sys.path.insert(0, str(backend_dir))

from app import app
