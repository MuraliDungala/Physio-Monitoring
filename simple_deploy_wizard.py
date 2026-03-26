#!/usr/bin/env python3
"""
SIMPLIFIED DEPLOYMENT ASSISTANT - Interactive guided deployment
No git/docker checks needed - focuses on web dashboard deployment
"""

import json
from datetime import datetime
from pathlib import Path

class SimpleDeploymentAssistant:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.deployment_log = self.project_root / "DEPLOYMENT_LOG.md"
        
    def log(self, message):
        """Log deployment step"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.deployment_log, 'a') as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70 + "\n")
    
    def step_1_verify_config(self):
        """Step 1: Verify configuration files"""
        self.print_header("📋 STEP 1: Verify Configuration Files")
        
        files = {
            "Backend config.py": self.project_root / "physio-web/backend/config.py",
            "Backend Dockerfile": self.project_root / "physio-web/backend/Dockerfile",
            "Frontend config.js": self.project_root / "physio-web/frontend/config.js",
            "Render config": self.project_root / "physio-web/render.yaml",
            ".gitignore": self.project_root / ".gitignore",
        }
        
        print("Checking deployment files:\n")
        all_good = True
        for name, path in files.items():
            if path.exists():
                print(f"  ✅ {name}")
            else:
                print(f"  ❌ {name} NOT FOUND")
                all_good = False
        
        if all_good:
            print("\n✅ All configuration files present!")
            self.log("Configuration files verified")
            return True
        else:
            print("\n⚠️  Some files missing!")
            return False
    
    def step_2_github_setup(self):
        """Step 2: GitHub setup instructions"""
        self.print_header("📤 STEP 2: Push to GitHub")
        
        print("""
You need to push your code to GitHub so Render/Vercel can access it.

Run these commands in PowerShell in your project folder:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Stage all changes:
   git add .

2. Commit changes:
   git commit -m "Production deployment configuration"

3. Push to GitHub:
   git push origin main

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Verify: Go to GitHub.com → Your Repo → Check recent commits

""")
        
        self.log("GitHub setup instructions shown")
        
        response = input("\n✅ Have you pushed to GitHub? (yes/no): ").strip().lower()
        return response == 'yes'
    
    def step_3_gather_secrets(self):
        """Step 3: Gather secrets and configuration"""
        self.print_header("🔐 STEP 3: Prepare Deployment Secrets")
        
        print("""
Your SECRET_KEY has already been generated:

  SECRET_KEY: 0QJ1jJhU_8NiB7kDbz8QX3OiKLcMTBn5Np6NZhEI0hM

This is in: DEPLOYMENT_SECRETS.md

Now you need to provide these values:
""")
        
        deploy_info = {}
        
        # Get GitHub URL
        print("\n1. Your GitHub Repository URL")
        print("   (Example: https://github.com/username/Physio-Monitoring)")
        github_url = input("   Enter URL: ").strip()
        deploy_info['github_url'] = github_url
        
        # Get database info
        print("\n2. PostgreSQL Connection String")
        print("   (Example: postgresql://user:pass@host:5432/dbname)")
        print("   Get this from Render.com or Railway.app PostgreSQL")
        db_url = input("   Enter DATABASE_URL: ").strip()
        deploy_info['database_url'] = db_url
        
        # Get Vercel domain (will be created)
        print("\n3. Your desired Vercel app name (for frontend)")
        print("   (Example: physio-app or physio-monitoring)")
        print("   Your URL will be: https://[name].vercel.app")
        vercel_name = input("   Enter app name: ").strip()
        deploy_info['vercel_name'] = vercel_name
        deploy_info['vercel_url'] = f"https://{vercel_name}.vercel.app"
        
        self.log("Deployment secrets gathered")
        return deploy_info
    
    def step_4_render_backend(self):
        """Step 4: Deploy Backend to Render"""
        self.print_header("🚀 STEP 4: Deploy Backend to Render")
        
        print("""
Now you'll deploy the backend to Render.com

Step-by-step:

1️⃣  Go to https://dashboard.render.com (login/create account)

2️⃣  Click "New" → "Web Service"

3️⃣  Paste your GitHub repository URL and click Connect

4️⃣  Configure these fields:
    
    Name:               physio-monitoring-backend
    Branch:             main
    Root Directory:     physio-web/backend
    Runtime:            Python 3
    Build Command:      pip install -r requirements.txt
    Start Command:      uvicorn app:app --host 0.0.0.0 --port $PORT

5️⃣  Scroll down and click "Add Environment Variable"
    
    Add each of these:
    ┌─────────────────────────────────────────────────┐
    │ ENVIRONMENT = production                        │
    │ SECRET_KEY = 0QJ1jJhU_8NiB7kDbz8QX3OiKLcMTBn5  │
    │               Np6NZhEI0hM                        │
    │ DATABASE_URL = [your database URL from step 3]  │
    │ CORS_ORIGINS = https://YOUR-VERCEL-NAME.       │
    │                vercel.app                       │
    │ PYTHONUNBUFFERED = 1                            │
    │ LOG_LEVEL = info                                │
    └─────────────────────────────────────────────────┘

6️⃣  Click "Create Web Service"

7️⃣  ⏳ Wait 2-3 minutes for deployment
    You'll see "Live" in green when ready

8️⃣  Copy your backend URL from the dashboard
    (Example: https://physio-backend-abc123.onrender.com)

""")
        
        self.log("Render backend deployment instructions shown")
        
        backend_url = input("\n📋 Enter your Render backend URL: ").strip()
        return backend_url
    
    def step_5_vercel_frontend(self, backend_url):
        """Step 5: Deploy Frontend to Vercel"""
        self.print_header("🌐 STEP 5: Deploy Frontend to Vercel")
        
        print(f"""
Now you'll deploy the frontend to Vercel.com

Step-by-step:

1️⃣  Go to https://vercel.com (login/create account)

2️⃣  Click "Add New..." → "Project"

3️⃣  Click "Continue with GitHub" and select your repository

4️⃣  Configure these fields:
    
    Framework:          Other (Static)
    Build Command:      (leave blank)
    Install Command:    (leave blank)
    Output Directory:   physio-web/frontend
    Root Directory:     .

5️⃣  Click "Deploy"

6️⃣  ⏳ Wait 1-2 minutes for deployment

7️⃣  After deployment completes:
    
    Go to Settings → Environment Variables
    
    Add these variables:
    ┌──────────────────────────────────────────┐
    │ REACT_APP_API_URL = {backend_url}       │
    │ REACT_APP_ENVIRONMENT = production      │
    │ REACT_APP_LOG_LEVEL = info              │
    └──────────────────────────────────────────┘

8️⃣  Go to Deployments → Select latest → Click "Redeploy"

9️⃣  ⏳ Wait for redeployment (1-2 minutes)

🔟 Copy your frontend URL from the dashboard
   (Example: https://physio-app-123.vercel.app)

""")
        
        self.log("Vercel frontend deployment instructions shown")
        
        frontend_url = input("\n📋 Enter your Vercel frontend URL: ").strip()
        return frontend_url
    
    def step_6_final_verification(self, backend_url, frontend_url):
        """Step 6: Final verification"""
        self.print_header("✨ STEP 6: Verify Deployment")
        
        print(f"""
Let's verify everything is working:

1️⃣  Test Backend Health Endpoint
    
    In your browser, go to:
    {backend_url}/health
    
    Expected: Page shows JSON with "status": "healthy"
    ✅ If it works, backend is live!
    ❌ If it fails, check Render logs

2️⃣  Access API Documentation
    
    In your browser, go to:
    {backend_url}/docs
    
    Expected: Swagger UI loads with all API endpoints
    ✅ If it works, API is documented!

3️⃣  Open Frontend Application
    
    In your browser, go to:
    {frontend_url}
    
    Expected: PhysioMonitor app loads without errors
    ✅ If it works, frontend is live!

4️⃣  Check Browser Console
    
    1. Open {frontend_url}
    2. Press F12 (open Developer Tools)
    3. Click "Console" tab
    4. Look for: "🔧 Frontend Configuration"
    5. Verify API URL shows: {backend_url}
    
    ✅ If API URL is correct, frontend detected backend!

5️⃣  Test Login
    
    1. Click "Login" on the app
    2. Create a test account
    3. Login should work
    
    ✅ If login works, database is connected!

""")
        
        self.log("Verification instructions shown")
        
        response = input("\n✅ Did all verification steps pass? (yes/no): ").strip().lower()
        return response == 'yes'
    
    def step_7_complete(self, backend_url, frontend_url):
        """Step 7: Deployment complete"""
        self.print_header("🎉 DEPLOYMENT COMPLETE!")
        
        print(f"""

Congratulations! Your app is now in production! 🚀

📊 Your Production URLs:

   Frontend:  {frontend_url}
   Backend:   {backend_url}
   API Docs:  {backend_url}/docs

💡 Next Steps (Optional):

   1. Set up custom domain (both Render & Vercel support this)
   2. Enable monitoring alerts in dashboards
   3. Monitor performance in Render/Vercel dashboards
   4. Set up database backups on Render
   5. Test all features from mobile devices

📚 Documentation:

   - DEPLOYMENT_GUIDE.md - Complete reference
   - ENV_VARIABLES.md - Variable reference
   - Render Docs - https://render.com/docs
   - Vercel Docs - https://vercel.com/docs

🔗 Dashboard Links:

   - Render: https://dashboard.render.com
   - Vercel: https://vercel.com/dashboard

""")
        
        self.log("Deployment successfully completed")
        print("✅ Deployment log saved to: DEPLOYMENT_LOG.md")
    
    def run(self):
        """Run the complete guided deployment"""
        self.print_header("🚀 PRODUCTION DEPLOYMENT ASSISTANT")
        
        print("""
Welcome! This wizard will guide you through deploying your 
Physiotherapy Monitoring System to production.

⏱️  Time: 30-45 minutes
📝 You'll deploy to: Render (backend) + Vercel (frontend)
💾 Database: PostgreSQL

Ready? Let's go! 🚀
""")
        
        try:
            # Step 1: Verify config
            if not self.step_1_verify_config():
                print("❌ Configuration files missing. Cannot continue.")
                return
            
            input("\n➡️  Press Enter to continue to GitHub setup...")
            
            # Step 2: GitHub
            if not self.step_2_github_setup():
                print("❌ Please push to GitHub first.")
                return
            
            input("\n➡️  Press Enter to continue to secrets...")
            
            # Step 3: Gather secrets
            deploy_info = self.step_3_gather_secrets()
            
            input("\n➡️  Press Enter to get Render instructions...")
            
            # Step 4: Render backend
            backend_url = self.step_4_render_backend()
            
            input("\n➡️  Press Enter to get Vercel instructions...")
            
            # Step 5: Vercel frontend
            frontend_url = self.step_5_vercel_frontend(backend_url)
            
            input("\n➡️  Press Enter to verify deployment...")
            
            # Step 6: Verify
            if not self.step_6_final_verification(backend_url, frontend_url):
                print("\n⚠️  Verification incomplete. Check the troubleshooting guide.")
                return
            
            # Step 7: Complete
            self.step_7_complete(backend_url, frontend_url)
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Deployment cancelled.")
            self.log("User cancelled deployment")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.log(f"Error: {e}")

def main():
    """Main entry point"""
    assistant = SimpleDeploymentAssistant()
    
    # Initialize log
    with open(assistant.deployment_log, 'w') as f:
        f.write(f"=== DEPLOYMENT LOG ===\nStarted: {datetime.now()}\n\n")
    
    assistant.run()

if __name__ == "__main__":
    main()
