import sys
import os
import importlib.util
from pathlib import Path

# Add backend directory to sys.path and change working directory
root_dir = Path(__file__).resolve().parent
backend_dir = root_dir / "physio-web" / "backend"

if backend_dir.exists():
    os.chdir(str(backend_dir))
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    backend_app_file = backend_dir / "app.py"
else:
    backend_app_file = root_dir / "app.py"

# Load backend app module without circular name clash
spec = importlib.util.spec_from_file_location("physio_backend_main", str(backend_app_file))
backend_module = importlib.util.module_from_spec(spec)
sys.modules["physio_backend_main"] = backend_module
spec.loader.exec_module(backend_module)

# Expose the FastAPI application instance
app = getattr(backend_module, "app")
