#!/usr/bin/env python3
"""
Pre-deployment verification script for Physio-Monitoring backend
Runs quick sanity checks before deploying to Render
"""

import subprocess
import sys
import time
import os
from pathlib import Path

# Colors for terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
END = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{END}")
    print(f"{BLUE}{text:^60}{END}")
    print(f"{BLUE}{'='*60}{END}\n")

def print_success(text):
    print(f"{GREEN}✅ {text}{END}")

def print_error(text):
    print(f"{RED}❌ {text}{END}")

def print_warning(text):
    print(f"{YELLOW}⚠️  {text}{END}")

def print_info(text):
    print(f"{BLUE}ℹ️  {text}{END}")

def check_file_exists(path):
    """Check if file exists"""
    if Path(path).exists():
        print_success(f"Found: {path}")
        return True
    else:
        print_error(f"Missing: {path}")
        return False

def check_python_imports():
    """Check if all required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'jose',
        'passlib',
        'cv2',
        'mediapipe'
    ]
    
    print_info("Checking Python imports...")
    all_ok = True
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"  {package}")
        except ImportError:
            print_error(f"  {package} - NOT INSTALLED")
            all_ok = False
    
    return all_ok

def check_backend_structure():
    """Check backend directory structure"""
    print_header("Checking Backend Structure")
    
    backend_dir = Path(__file__).parent / "physio-web" / "backend"
    
    required_files = [
        "app.py",
        "config.py",
        "auth.py",
        "requirements.txt",
        "runtime.txt",
        "Procfile",
        "render.yaml"
    ]
    
    all_found = True
    for file in required_files:
        if not check_file_exists(backend_dir / file):
            all_found = False
    
    return all_found

def check_imports_in_code():
    """Check if app.py can be imported"""
    print_header("Checking App.py Import")
    
    try:
        # Add backend to path
        backend_path = Path(__file__).parent / "physio-web" / "backend"
        sys.path.insert(0, str(backend_path))
        
        # Try importing app
        import app
        print_success("app.py imports successfully")
        
        # Check if FastAPI instance exists
        if hasattr(app, 'app'):
            print_success("FastAPI instance 'app' found")
            return True
        else:
            print_warning("FastAPI instance 'app' not found")
            return False
            
    except Exception as e:
        print_error(f"Failed to import app.py: {e}")
        return False

def check_env_file():
    """Check .env.production file"""
    print_header("Checking Environment Configuration")
    
    env_file = Path(__file__).parent / "physio-web" / "backend" / ".env.production"
    
    if env_file.exists():
        print_success("Found .env.production")
        with open(env_file) as f:
            content = f.read()
            if 'SECRET_KEY' in content:
                print_success("SECRET_KEY defined")
            else:
                print_warning("SECRET_KEY not defined - will need to add on Render")
        return True
    else:
        print_warning(".env.production not found - will set vars on Render")
        return False

def check_requirements():
    """Verify requirements.txt is complete"""
    print_header("Checking Requirements")
    
    req_file = Path(__file__).parent / "physio-web" / "backend" / "requirements.txt"
    
    if not req_file.exists():
        print_error("requirements.txt not found!")
        return False
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'python-jose',
        'passlib',
        'opencv-python',
        'mediapipe'
    ]
    
    with open(req_file) as f:
        content = f.read()
    
    all_required = True
    for package in required_packages:
        if package.lower() in content.lower():
            print_success(f"  {package}")
        else:
            print_warning(f"  {package} - not found")
            all_required = False
    
    return all_required

def check_procfile():
    """Verify Procfile is valid"""
    print_header("Checking Procfile")
    
    procfile = Path(__file__).parent / "physio-web" / "backend" / "Procfile"
    
    if not procfile.exists():
        print_error("Procfile not found!")
        return False
    
    with open(procfile) as f:
        content = f.read().strip()
    
    if 'uvicorn' in content and 'app:app' in content:
        print_success(f"Procfile content: {content}")
        return True
    else:
        print_error("Procfile doesn't contain proper uvicorn command")
        return False

def run_all_checks():
    """Run all verification checks"""
    print_header("Physio-Monitoring Backend - Pre-Deployment Verification")
    print_info("Running verification checks...\n")
    
    checks = [
        ("Backend Directory Structure", check_backend_structure),
        ("Requirements.txt", check_requirements),
        ("Procfile Configuration", check_procfile),
        ("Environment Configuration", check_env_file),
        ("Python Imports Available", check_python_imports),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_error(f"Error during {check_name}: {e}")
            results.append((check_name, False))
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = f"{GREEN}✅ PASS{END}" if result else f"{RED}❌ FAIL{END}"
        print(f"{status} - {check_name}")
    
    print(f"\n{BLUE}{'='*60}{END}")
    if passed == total:
        print_success(f"All checks passed! ({passed}/{total})")
        print(f"{GREEN}Backend is ready for deployment to Render{END}")
        return True
    else:
        print_warning(f"Some checks failed ({passed}/{total})")
        print(f"{YELLOW}Please fix issues before deploying{END}")
        return False

if __name__ == "__main__":
    print("\n")
    success = run_all_checks()
    print("\n")
    sys.exit(0 if success else 1)
