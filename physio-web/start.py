#!/usr/bin/env python3
"""
Physiotherapy Monitoring System - Startup Script
"""

import os
import sys
import subprocess
import time
import webbrowser
from pathlib import Path

def check_python_version():
    """Check Python version compatibility"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version}")

def check_dependencies():
    """Check if required packages are installed"""
    print("🔍 Checking dependencies...")
    
    backend_requirements = [
        "fastapi", "uvicorn", "websockets", "sqlalchemy",
        "opencv-python", "mediapipe", "numpy", "scikit-learn",
        "pandas", "matplotlib", "seaborn", "h5py"
    ]
    
    missing_packages = []
    
    package_mapping = {
        "opencv-python": "cv2",
        "scikit-learn": "sklearn"
    }
    
    for package in backend_requirements:
        try:
            module_name = package_mapping.get(package, package.replace("-", "_"))
            __import__(module_name)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"
            ] + missing_packages)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            print("Please run: pip install -r backend/requirements.txt")
            return False
    
    return True

def setup_environment():
    """Setup environment variables"""
    backend_dir = Path("backend")
    env_file = backend_dir / ".env"
    env_example = backend_dir / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from example...")
        import shutil
        shutil.copy(env_example, env_file)
        print("✅ .env file created")
        print("⚠️  Please review and update .env file with your settings")
    
    return True

def init_database():
    """Initialize database with exercises"""
    print("🗄️  Initializing database...")
    backend_dir = Path("backend")
    init_script = backend_dir / "init_db.py"
    
    if not init_script.exists():
        print("⚠️  Database initialization script not found")
        return False
    
    try:
        # Run init script from project root without changing directory
        result = subprocess.run([
            sys.executable, str(init_script.absolute())
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(result.stdout)
            return True
        else:
            print(f"❌ Database initialization failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting backend server...")
    
    backend_dir = Path("backend")
    app_file = backend_dir / "app.py"
    
    if not app_file.exists():
        print("❌ Backend app.py not found")
        return None
    
    try:
        # Change to backend directory
        os.chdir(backend_dir)
        
        # Start uvicorn server
        process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
        
        print("✅ Backend server started on http://localhost:8000")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the frontend static file server"""
    print("🌐 Starting frontend server...")
    
    # Get absolute path to frontend directory from project root
    project_root = Path(__file__).parent
    frontend_dir = project_root / "frontend"
    
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found at: {frontend_dir}")
        return None
    
    try:
        # Start Python HTTP server without changing directory
        process = subprocess.Popen([
            sys.executable, "-m", "http.server", "3000"
        ], cwd=str(frontend_dir))
        
        print("✅ Frontend server started on http://localhost:3000")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def wait_for_servers():
    """Wait for servers to be ready"""
    import urllib.request
    import urllib.error
    
    print("⏳ Waiting for servers to start...")
    
    backend_url = "http://localhost:8001/health"
    frontend_url = "http://localhost:3000"
    
    # Wait for backend
    for i in range(30):  # Wait up to 30 seconds
        try:
            urllib.request.urlopen(backend_url)
            print("✅ Backend server is ready")
            break
        except urllib.error.URLError:
            time.sleep(1)
    else:
        print("⚠️  Backend server not ready, but continuing...")
    
    # Wait for frontend
    for i in range(30):  # Wait up to 30 seconds
        try:
            urllib.request.urlopen(frontend_url)
            print("✅ Frontend server is ready")
            break
        except urllib.error.URLError:
            time.sleep(1)
    else:
        print("⚠️  Frontend server not ready, but continuing...")

def open_browser():
    """Open browser with the application"""
    print("🌍 Opening browser...")
    try:
        webbrowser.open("http://localhost:8001")
        print("✅ Browser opened")
    except Exception as e:
        print(f"⚠️  Could not open browser: {e}")
        print("Please manually open: http://localhost:8001")

def main():
    """Main startup function"""
    print("=" * 60)
    print("🏥 Physiotherapy Monitoring System - Startup")
    print("=" * 60)
    
    # Check prerequisites
    check_python_version()
    
    if not check_dependencies():
        print("❌ Dependency check failed")
        sys.exit(1)
    
    setup_environment()
    
    # Initialize database
    if not init_database():
        print("⚠️  Database initialization had issues, continuing anyway...")
    
    # Start servers
    backend_process = start_backend()
    frontend_process = start_frontend()
    
    if not backend_process or not frontend_process:
        print("❌ Failed to start servers")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        sys.exit(1)
    
    # Wait for servers to be ready
    wait_for_servers()
    
    # Open browser
    open_browser()
    
    print("\n" + "=" * 60)
    print("🎉 System is running!")
    print("📱 Frontend: http://localhost:3000")
    print("🔧 Backend API: http://localhost:8001")
    print("📚 API Docs: http://localhost:8001/docs")
    print("=" * 60)
    print("⏹️  Press Ctrl+C to stop the servers")
    
    try:
        # Wait for user interrupt
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️  Shutting down servers...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
            print("✅ Backend server stopped")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend server stopped")
        
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
