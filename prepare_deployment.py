#!/usr/bin/env python3
"""
Deployment preparation script - Run this before deploying to production
"""

import os
import sys
import secrets
import subprocess
from pathlib import Path

def generate_secret_key():
    """Generate a secure secret key for production"""
    return secrets.token_urlsafe(32)

def check_git_status():
    """Check if git is initialized and all files are committed"""
    print("\n📦 Checking Git Status...")
    
    if not Path(".git").exists():
        print("❌ Git not initialized. Initializing...")
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "Initial deployment setup"], check=True)
        print("✅ Git initialized and committed")
    else:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.stdout.strip():
            print("⚠️ Uncommitted changes detected:")
            print(result.stdout)
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                sys.exit(1)
        else:
            print("✅ All changes committed")

def check_backend_config():
    """Check backend configuration"""
    print("\n🔧 Checking Backend Configuration...")
    
    backend_dir = Path("physio-web/backend")
    
    # Check .env
    env_file = backend_dir / ".env"
    if env_file.exists():
        with open(env_file) as f:
            content = f.read()
            if "CHANGE_THIS_IN_PRODUCTION" in content or "your-secret-key" in content.lower():
                print("❌ .env contains placeholder values. Please update it.")
                return False
    else:
        print("⚠️ .env not found, creating from example...")
        env_example = backend_dir / ".env.example"
        if env_example.exists():
            with open(env_example) as src, open(env_file, 'w') as dst:
                dst.write(src.read())
            print("✅ .env created from .env.example")
        else:
            print("❌ .env.example not found")
            return False
    
    # Check config.py
    if (backend_dir / "config.py").exists():
        print("✅ config.py found")
    else:
        print("❌ config.py not found")
        return False
    
    # Check Dockerfile
    if (backend_dir / "Dockerfile").exists():
        print("✅ Dockerfile found")
    else:
        print("❌ Dockerfile not found")
        return False
    
    return True

def check_frontend_config():
    """Check frontend configuration"""
    print("\n🌐 Checking Frontend Configuration...")
    
    frontend_dir = Path("physio-web/frontend")
    
    # Check config.js
    if (frontend_dir / "config.js").exists():
        print("✅ config.js found")
    else:
        print("❌ config.js not found")
        return False
    
    # Check .env files
    if (frontend_dir / ".env.example").exists():
        print("✅ .env.example found")
    else:
        print("❌ .env.example not found")
        return False
    
    if (frontend_dir / ".env.production").exists():
        print("✅ .env.production found")
    else:
        print("⚠️ .env.production not found (will be created)")
    
    return True

def create_deployment_checklist():
    """Generate deployment checklist"""
    print("\n📋 Generating Deployment Checklist...")
    
    checklist_content = """# Deployment Checklist

## Pre-Deployment (Local)

### Backend Setup
- [ ] python -m pip install --upgrade pip
- [ ] python -m pip install -r physio-web/backend/requirements.txt
- [ ] Generate SECRET_KEY: python -c "import secrets; print(secrets.token_urlsafe(32))"
- [ ] Update .env with generated SECRET_KEY
- [ ] Update DATABASE_URL to production database string
- [ ] Test backend locally: python -m uvicorn physio-web/backend/app:app
- [ ] Check API docs: http://localhost:8000/docs
- [ ] Health check: curl http://localhost:8000/health

### Frontend Setup
- [ ] Update frontend .env.production with production API URL
- [ ] Test frontend locally with: python -m http.server 3000 --directory physio-web/frontend
- [ ] Check API_BASE_URL in browser console

### Database Setup
- [ ] Create PostgreSQL database (Render or Railway)
- [ ] Note connection string
- [ ] Test connection locally before deploying

### Git Setup
- [ ] git add .
- [ ] git commit -m "Production deployment configuration"
- [ ] git push origin main

## Deployment (Remote)

### Backend Deployment (Render)

1. On Render.com:
   - [ ] New Web Service
   - [ ] Connect GitHub
   - [ ] Runtime: Python 3
   - [ ] Build Command: pip install -r requirements.txt
   - [ ] Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
   - [ ] Root Directory: physio-web/backend
   - [ ] Environment Variables:
     - ENVIRONMENT=production
     - SECRET_KEY=<generated-key>
     - DATABASE_URL=<production-db-url>
     - CORS_ORIGINS=https://your-frontend.vercel.app
     - PYTHONUNBUFFERED=1

### Frontend Deployment (Vercel)

1. On Vercel.com:
   - [ ] Import GitHub repository
   - [ ] Framework: Other (Static)
   - [ ] Output Directory: physio-web/frontend
   - [ ] Environment Variables:
     - REACT_APP_API_URL=https://your-backend.onrender.com
     - REACT_APP_ENVIRONMENT=production
   - [ ] Redeploy after setting env vars

## Post-Deployment

### Backend Verification
- [ ] Health endpoint returns 200: https://your-backend.onrender.com/health
- [ ] API docs accessible: https://your-backend.onrender.com/docs
- [ ] Check deployment logs for errors
- [ ] Test database connection
- [ ] Verify environment variables are set

### Frontend Verification
- [ ] Frontend loads without errors
- [ ] Check browser console for API configuration
- [ ] Verify API_BASE_URL points to production backend
- [ ] Test login/registration
- [ ] Test WebSocket connection
- [ ] Test exercise features

### Connection Verification
- [ ] Frontend can communicate with backend
- [ ] CORS headers are correct
- [ ] All API endpoints working
- [ ] WebSocket connection established

## Post-Deployment Monitoring

- [ ] Set up error alerts (Render/Railway dashboard)
- [ ] Monitor API logs
- [ ] Check performance metrics
- [ ] Test from multiple devices/browsers
- [ ] Verify SSL/TLS certificates (auto-managed)

## Rollback Plan (if needed)

- [ ] Previous commit hash recorded
- [ ] Rolling back to previous git commit
- [ ] Triggering redeployment on Render/Vercel
"""
    
    checklist_path = Path("DEPLOYMENT_CHECKLIST.md")
    with open(checklist_path, 'w') as f:
        f.write(checklist_content)
    
    print(f"✅ Checklist saved to: {checklist_path}")

def create_secrets_config():
    """Create secrets configuration guide"""
    print("\n🔐 Creating Secrets Configuration Guide...")
    
    secrets_guide = f"""# Production Secrets Configuration

## Generated at: {Path('SECRETS.txt').name}

### Backend Secrets

#### SECRET_KEY (for JWT)
Run this command and save the output:
```
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Example output: `Y8x9mK2pL5vJ3nQ1wR6tU9bD4fG7cH0aE2sL8pK5jH3xN`

Store this in:
- Render: Environment Variables
- Railway: Variables
- File: physio-web/backend/.env

#### Database Credentials
You must provide separate credentials for:
1. Username (e.g., physio_user)
2. Password (generate a strong one)
3. Host (provided by database service)
4. Port (usually 5432)
5. Database name (e.g., physio_monitoring_prod)

### Frontend Configuration

#### API_BASE_URL
Set to your deployed backend URL:
- Example: https://physio-monitoring-backend.onrender.com
- Use in: Frontend Environment Variables

### Environment Variables Summary

#### Backend (.env or Render/Railway Variables)
```
ENVIRONMENT=production
SECRET_KEY=<your-secret-key>
DATABASE_URL=postgresql://username:password@host:port/dbname
CORS_ORIGINS=https://your-frontend.vercel.app,https://your-domain.com
PORT=8000
PYTHONUNBUFFERED=1
LOG_LEVEL=info
```

#### Frontend (.env.production or Vercel/Netlify Variables)
```
REACT_APP_API_URL=https://your-backend.onrender.com
REACT_APP_ENVIRONMENT=production
REACT_APP_LOG_LEVEL=info
```

### Security Reminders

⚠️ IMPORTANT:

1. **NEVER** commit .env or secrets to GitHub
2. **NEVER** share your SECRET_KEY
3. **NEVER** publish database passwords
4. **ALWAYS** use strong passwords (20+ characters)
5. **ALWAYS** verify CORS_ORIGINS match your deploy domains
6. **ALWAYS** use HTTPS (enabled automatically by Render/Vercel)
7. **ALWAYS** keep sensitive data in environment variables, never in code

### Credential Rotation

When rotating credentials:
1. Update in deployment platform first
2. Redeploy application
3. Update in GitHub secrets (if using CI/CD)
4. Delete old credentials from database

"""
    
    secrets_path = Path("SECRETS_CONFIGURATION.md")
    with open(secrets_path, 'w') as f:
        f.write(secrets_guide)
    
    print(f"✅ Secrets guide saved to: {secrets_path}")

def print_deployment_summary():
    """Print deployment summary"""
    print("\n" + "="*60)
    print("✅ DEPLOYMENT PREPARATION COMPLETE")
    print("="*60)
    print("\nNext Steps:")
    print("1. Update backend .env with database credentials")
    print("2. Generate SECRET_KEY: python -c \"import secrets; print(secrets.token_urlsafe(32))\"")
    print("3. Push to GitHub: git push origin main")
    print("4. Deploy backend to Render/Railway")
    print("5. Deploy frontend to Vercel/Netlify")
    print("6. Set environment variables in each platform")
    print("7. Verify deployment with checklist")
    print("\nFor detailed instructions, see: DEPLOYMENT_GUIDE.md")
    print("For checklist, see: DEPLOYMENT_CHECKLIST.md")
    print("For secrets config, see: SECRETS_CONFIGURATION.md")
    print("="*60 + "\n")

def main():
    """Main deployment preparation"""
    print("🚀 Deployment Preparation Script")
    print("=" * 60)
    
    try:
        check_git_status()
        backend_ok = check_backend_config()
        frontend_ok = check_frontend_config()
        
        if backend_ok and frontend_ok:
            create_deployment_checklist()
            create_secrets_config()
            print_deployment_summary()
        else:
            print("\n❌ Configuration check failed. Please fix issues above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error during preparation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
