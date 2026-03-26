#!/usr/bin/env python3
"""
Quick Deployment Guide - Copy-paste commands for each step
"""

import platform

def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def print_step(number, title):
    print(f"\n📍 STEP {number}: {title}")
    print('-' * 70)

def main():
    os_type = platform.system()
    
    print_header("🚀 QUICK DEPLOYMENT GUIDE - Commands to Run")
    
    print("""
This guide provides copy-paste commands for deploying to production.
Follow each step in order.
""")
    
    print_step(1, "Initialize Git & Push to GitHub")
    print("""
# Navigate to project root
cd ~/Desktop/Physio-Monitoring

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial deployment configuration"
git branch -M main

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/Physio-Monitoring.git
git push -u origin main

# Verify push was successful
git log --oneline  # Should show your commits
""")
    
    print_step(2, "Set up Backend Environment")
    print("""
# Navigate to backend
cd physio-web/backend

# Generate SECRET_KEY (copy the output)
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Copy example env file
cp .env.example .env

# Edit .env file with:
# - SECRET_KEY from above
# - DATABASE_URL from your provider (Render or Railway PostgreSQL)
# - ENVIRONMENT=production
# - PORT=8000
# - CORS_ORIGINS=https://your-frontend.vercel.app

# Test locally
python -m uvicorn app:app --host 0.0.0.0 --port 8000

# Check health endpoint
curl http://localhost:8000/health
""")
    
    print_step(3, "Deploy Backend to Render")
    print("""
1. Sign up at https://render.com
2. Connect your GitHub account

3. Click "New" → "Web Service"
4. Select your Physio-Monitoring repository

5. Configure:
   - Name: physio-monitoring-backend
   - Runtime: Python 3
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
   - Root Directory: physio-web/backend

6. Click "Create Web Service"

7. After creation, go to "Environment" tab and add:
   - ENVIRONMENT: production
   - SECRET_KEY: <your-generated-key>
   - DATABASE_URL: postgresql://...
   - CORS_ORIGINS: https://your-frontend.vercel.app
   - PORT: 8000
   - PYTHONUNBUFFERED: 1

8. Save and monitor deployment
9. Copy the service URL (e.g., https://physio-monitoring-backend.onrender.com)
""")
    
    print_step(4, "Deploy Frontend to Vercel")
    print("""
1. Sign up at https://vercel.com
2. Click "Add New..." → "Project"
3. Import your GitHub repository

4. Configure:
   - Framework: Other (Static)
   - Build Command: (leave blank)
   - Output Directory: physio-web/frontend
   - Root Directory: .

5. Click "Deploy"

6. After deployment, go to Settings → Environment Variables
7. Add:
   - REACT_APP_API_URL: https://your-backend.onrender.com
   - REACT_APP_ENVIRONMENT: production

8. Go to Deployments → Redeploy to apply env vars

9. Copy the frontend URL (e.g., https://your-app.vercel.app)
""")
    
    print_step(5, "Update Backend CORS Settings")
    print("""
Back to Render Dashboard:

1. Go to your backend service
2. Environment tab
3. Update CORS_ORIGINS to include your frontend URL:
   https://your-app.vercel.app

4. Click "Save"
5. Service will automatically redeploy

Now both frontend and backend can communicate!
""")
    
    print_step(6, "Test Deployment")
    print("""
# Test backend health
curl https://your-backend.onrender.com/health

# Expected response:
# {"status":"healthy","environment":"production","version":"1.0.0","timestamp":"..."}

# Access API Documentation
# Open in browser: https://your-backend.onrender.com/docs

# Test frontend
# Open in browser: https://your-app.vercel.app

# In browser console (F12), you should see:
# "🔧 Frontend Configuration"
# with API Base URL pointing to your backend

# Try logging in to test API connectivity
""")
    
    print_step(7, "Troubleshooting")
    print("""
If frontend can't reach backend (CORS error):

1. Check CORS_ORIGINS includes frontend domain exactly
2. Redeploy backend after updating CORS_ORIGINS
3. Clear browser cache (Ctrl+Shift+Delete)
4. Check browser console for actual error message

Example correct CORS_ORIGINS:
CORS_ORIGINS=https://your-app.vercel.app,https://www.your-app.vercel.app

If health check fails:
1. Check backend logs in Render dashboard
2. Verify DATABASE_URL is correct
3. Verify SECRET_KEY is set
""")
    
    print_header("✅ DEPLOYMENT COMPLETE")
    print("""
All services are now deployed to production!

🌐 Frontend URL: https://your-app.vercel.app
⚙️  Backend API: https://your-backend.onrender.com
📚 API Docs: https://your-backend.onrender.com/docs

Your application is live and accessible to users.
Monitor deployments in Render and Vercel dashboards.
""")

if __name__ == "__main__":
    main()
