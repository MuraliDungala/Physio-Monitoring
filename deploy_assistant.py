#!/usr/bin/env python3
"""
AUTOMATED DEPLOYMENT ASSISTANT - Interactive guided deployment to Render/Vercel
Run this script and follow the prompts
"""

import os
import sys
import subprocess
import webbrowser
import json
from pathlib import Path
from datetime import datetime

class DeploymentAssistant:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.deployment_log = self.project_root / "DEPLOYMENT_LOG.md"
        self.secrets_file = self.project_root / "DEPLOYMENT_SECRETS.json"
        
    def log(self, message, level="INFO"):
        """Log deployment steps"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}\n"
        with open(self.deployment_log, 'a') as f:
            f.write(log_entry)
        print(log_entry.strip())
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*70)
        print(f"  {title}")
        print("="*70 + "\n")
    
    def print_step(self, number, title):
        """Print step indicator"""
        print(f"\n📍 STEP {number}: {title}")
        print("-" * 70)
    
    def check_prerequisites(self):
        """Check if prerequisites are met"""
        self.print_header("🔍 Checking Prerequisites")
        
        checks = {
            "GitHub Account": "https://github.com",
            "Render Account": "https://render.com",
            "Vercel Account": "https://vercel.com",
            "Git installed": self.check_git(),
            "Docker installed": self.check_docker(),
        }
        
        print("\n✅ Prerequisites Check:\n")
        all_met = True
        for check, status in checks.items():
            if isinstance(status, bool):
                status_str = "✅" if status else "❌"
                print(f"  {status_str} {check}")
                if not status:
                    all_met = False
            else:
                print(f"  📝 {check}: {status}")
        
        if not all_met:
            print("\n⚠️  Some checks failed. Install required tools before continuing.")
            return False
        
        self.log("Prerequisites check passed", "SUCCESS")
        return True
    
    def check_git(self):
        """Check if git is installed"""
        try:
            subprocess.run(["git", "--version"], capture_output=True, check=True)
            return True
        except:
            return False
    
    def check_docker(self):
        """Check if docker is installed"""
        try:
            subprocess.run(["docker", "--version"], capture_output=True, check=True)
            return True
        except:
            return False
    
    def step_1_verify_files(self):
        """Step 1: Verify all deployment files"""
        self.print_step(1, "Verify Deployment Files")
        
        required_files = {
            "Backend Config": "physio-web/backend/config.py",
            "Backend Dockerfile": "physio-web/backend/Dockerfile",
            "Frontend Config": "physio-web/frontend/config.js",
            "Render Config": "physio-web/render.yaml",
            "Docker Compose": "docker-compose.yml",
            ".gitignore": ".gitignore",
        }
        
        print("\n✅ Checking files:\n")
        all_present = True
        for name, path in required_files.items():
            file_path = self.project_root / path
            if file_path.exists():
                print(f"  ✅ {name}: {path}")
            else:
                print(f"  ❌ {name}: {path} (MISSING)")
                all_present = False
        
        if all_present:
            print("\n✅ All deployment files present!")
            self.log("All deployment files verified", "SUCCESS")
            return True
        else:
            print("\n❌ Some files are missing!")
            self.log("Missing deployment files", "ERROR")
            return False
    
    def step_2_create_secrets(self):
        """Step 2: Create and save secrets"""
        self.print_step(2, "Create Production Secrets")
        
        print("\n🔑 Generating production secrets...\n")
        
        # Generate SECRET_KEY
        try:
            result = subprocess.run(
                ["python", "-c", "import secrets; print(secrets.token_urlsafe(32))"],
                capture_output=True,
                text=True,
                check=True
            )
            secret_key = result.stdout.strip()
        except:
            secret_key = "FAILED_TO_GENERATE"
        
        secrets = {
            "generated_at": datetime.now().isoformat(),
            "backend": {
                "SECRET_KEY": secret_key,
                "ENVIRONMENT": "production",
                "PORT": "8000",
                "PYTHONUNBUFFERED": "1",
                "LOG_LEVEL": "info",
            },
            "frontend": {
                "REACT_APP_ENVIRONMENT": "production",
                "REACT_APP_LOG_LEVEL": "info",
            },
            "required_input": {
                "DATABASE_URL": "postgresql://user:pass@host:5432/dbname",
                "CORS_ORIGINS": "https://your-frontend.vercel.app",
                "REACT_APP_API_URL": "https://your-backend.onrender.com",
            }
        }
        
        print("✅ Generated Secrets:\n")
        print(f"  SECRET_KEY: {secret_key[:20]}...{secret_key[-10:]}")
        print(f"  ENVIRONMENT: production")
        print(f"  PYTHONUNBUFFERED: 1")
        
        # Save secrets
        with open(self.secrets_file, 'w') as f:
            json.dump(secrets, f, indent=2)
        
        print(f"\n💾 Secrets saved to: {self.secrets_file}")
        print("\n⚠️  You must provide these values for production:")
        print(f"  1. DATABASE_URL (from Render/Railway PostgreSQL)")
        print(f"  2. CORS_ORIGINS (your Vercel frontend domain)")
        print(f"  3. REACT_APP_API_URL (your Render backend domain)")
        
        self.log("Secrets generated", "SUCCESS")
        return secrets
    
    def step_3_git_push(self):
        """Step 3: Push to GitHub"""
        self.print_step(3, "Push Configuration to GitHub")
        
        print("\n📤 Git commands to run:\n")
        
        commands = [
            ("git add .", "Stage all changes"),
            ('git commit -m "Production deployment configuration"', "Commit changes"),
            ("git push origin main", "Push to GitHub"),
        ]
        
        for cmd, description in commands:
            print(f"  {description}:")
            print(f"    $ {cmd}\n")
        
        print("\n⚠️  Run these commands in terminal:")
        print("```bash")
        for cmd, _ in commands:
            print(cmd)
        print("```")
        
        self.log("Git push instructions provided", "INFO")
    
    def step_4_render_deployment(self):
        """Step 4: Deploy to Render"""
        self.print_step(4, "Deploy Backend to Render")
        
        print("""

1️⃣  Go to https://render.com and sign up/log in

2️⃣  Click "New" → "Web Service"

3️⃣  Select your GitHub repository (Physio-Monitoring)

4️⃣  Configure the service:
    
    Name:                  physio-monitoring-backend
    Branch:                main
    Runtime:               Python 3
    Root Directory:        physio-web/backend
    Build Command:         pip install -r requirements.txt
    Start Command:         uvicorn app:app --host 0.0.0.0 --port $PORT

5️⃣  Click "Create Web Service"

6️⃣  After creation, go to "Environment" tab

7️⃣  Add these environment variables:
    
    ENVIRONMENT:          production
    SECRET_KEY:           <from DEPLOYMENT_SECRETS.json>
    DATABASE_URL:         <your-postgresql-url>
    CORS_ORIGINS:         https://your-frontend.vercel.app
    PYTHONUNBUFFERED:     1
    LOG_LEVEL:            info

8️⃣  Click "Save"

9️⃣  Wait for deployment to complete
    ⏳ Typical time: 2-3 minutes
    ✅ You'll see "Live" when ready

📝 Copy your backend URL from the dashboard
   Example: https://physio-monitoring-backend.onrender.com

""")
        
        print("\n⏳ Waiting for Render deployment...")
        print("💡 Tip: Monitor progress in Render dashboard → Logs")
        
        self.log("Render deployment instructions provided", "INFO")
    
    def step_5_vercel_deployment(self):
        """Step 5: Deploy to Vercel"""
        self.print_step(5, "Deploy Frontend to Vercel")
        
        backend_url = input("\n📥 Enter your Render backend URL: ").strip()
        
        print(f"""

1️⃣  Go to https://vercel.com and sign up/log in

2️⃣  Click "Add New..." → "Project"

3️⃣  Select your GitHub repository (Physio-Monitoring)

4️⃣  Configure the project:
    
    Framework:           Other (Static)
    Build Command:       (leave blank)
    Output Directory:    physio-web/frontend
    Root Directory:      .

5️⃣  Click "Deploy"

6️⃣  After deployment, go to "Settings" → "Environment Variables"

7️⃣  Add these variables:
    
    REACT_APP_API_URL:       {backend_url}
    REACT_APP_ENVIRONMENT:   production
    REACT_APP_LOG_LEVEL:     info

8️⃣  Click "Save"

9️⃣  Go to "Deployments" → Click three dots → "Redeploy"

🔟 Wait for deployment complete

📝 Copy your frontend URL from the dashboard
   Example: https://your-app.vercel.app

""")
        
        self.log(f"Vercel deployment instructions provided with backend URL: {backend_url}", "INFO")
    
    def step_6_verify_deployment(self):
        """Step 6: Verify deployment"""
        self.print_step(6, "Verify Production Deployment")
        
        backend_url = input("📥 Enter your Render backend URL: ").strip()
        frontend_url = input("📥 Enter your Vercel frontend URL: ").strip()
        
        print(f"""

🔍 Verification Checklist:

1️⃣  Health Check Backend:
    
    Command: curl {backend_url}/health
    
    Expected:
    Status: 200
    Response: {{"status":"healthy",...}}

2️⃣  Access API Documentation:
    
    URL: {backend_url}/docs
    
    Expected: Swagger UI loads

3️⃣  Open Frontend:
    
    URL: {frontend_url}
    
    Expected: App loads without errors

4️⃣  Check Browser Console:
    
    1. Open {frontend_url}
    2. Press F12 (Developer Tools)
    3. Check Console tab
    4. Look for: "🔧 Frontend Configuration"
    5. Verify API_BASE_URL: {backend_url}

5️⃣  Test Login:
    
    1. Create test account
    2. Login should work
    3. No CORS errors

6️⃣  Test Exercise Detection:
    
    1. Grant camera permission
    2. Start exercise session
    3. WebSocket should connect
    4. Real-time detection should work

✅ If all checks pass: DEPLOYMENT SUCCESSFUL!

""")
        
        self.log(f"Deployment verification initiated", "INFO")
    
    def step_7_troubleshoot(self):
        """Step 7: Troubleshooting guide"""
        self.print_step(7, "Troubleshooting")
        
        print("""

❌ Common Issues & Solutions:

1. CORS Errors ("Access to XMLHttpRequest blocked")
   
   Solution:
   - Check CORS_ORIGINS environment variable
   - Must match your frontend domain exactly
   - Wait 2-3 minutes for Render to redeploy
   - Clear browser cache (Ctrl+Shift+Delete)

2. 502 Bad Gateway on Backend
   
   Solution:
   - Check Render dashboard logs
   - Verify DATABASE_URL is correct
   - Verify SECRET_KEY is set
   - Restart service in Render dashboard

3. "Cannot reach backend" / "API not responding"
   
   Solution:
   - Verify REACT_APP_API_URL is correct
   - Redeploy frontend after setting env vars
   - Wait 2-3 minutes for Vercel
   - Check that backend URL is live (test health endpoint)

4. Database Connection Failed
   
   Solution:
   - Verify DATABASE_URL format
   - Test connection string locally
   - Check database credentials
   - Ensure database service is running

5. "WebSocket connection failed"
   
   Solution:
   - Backend must be accessible via HTTPS
   - Check Render deployment is complete
   - Verify no firewall blocking WebSocket

📞 Get Help:
   - Check DEPLOYMENT_GUIDE.md
   - Review Render logs: Dashboard → [Service] → Logs
   - Review Vercel logs: Dashboard → Deployments → [Deployment]

""")
        
        self.log("Troubleshooting guide displayed", "INFO")
    
    def run_guided_deployment(self):
        """Run the complete guided deployment"""
        self.print_header("🚀 AUTOMATED PRODUCTION DEPLOYMENT ASSISTANT")
        
        print("""
This script will guide you through deploying to Render (backend) and 
Vercel (frontend) with step-by-step instructions.

⏱️  Estimated time: 30-45 minutes
📝 You'll need: GitHub, Render, Vercel accounts, PostgreSQL URL

""")
        
        response = input("Ready to start deployment? (yes/no): ").strip().lower()
        if response != 'yes':
            print("Deployment cancelled.")
            return
        
        # Run steps
        try:
            if not self.check_prerequisites():
                print("\n❌ Prerequisites not met. Please install required tools.")
                return
            
            if not self.step_1_verify_files():
                print("\n❌ Deployment files missing. Setup incomplete.")
                return
            
            secrets = self.step_2_create_secrets()
            input("\n➡️  Press Enter to continue to GitHub...")
            
            self.step_3_git_push()
            input("\n➡️  After pushing to GitHub, press Enter to continue...")
            
            self.step_4_render_deployment()
            input("\n➡️  After deploying to Render, press Enter to continue...")
            
            self.step_5_vercel_deployment()
            input("\n➡️  After deploying to Vercel, press Enter to continue...")
            
            self.step_6_verify_deployment()
            input("\n➡️  Press Enter to see troubleshooting guide...")
            
            self.step_7_troubleshoot()
            
            self.print_header("✅ DEPLOYMENT COMPLETE!")
            print(f"""
Congratulations! Your application is now deployed to production!

📝 Deployment Summary:
   Backend:  Render.com
   Frontend: Vercel
   Database: PostgreSQL

📊 Monitor Your Services:
   Render Dashboard:  https://dashboard.render.com
   Vercel Dashboard:  https://vercel.com/dashboard

📋 Documentation:
   - DEPLOYMENT_GUIDE.md
   - TROUBLESHOOTING.md
   - ENV_VARIABLES.md

🔐 Secrets saved to: {self.secrets_file}

""")
            
            self.log("Deployment assistance completed successfully", "SUCCESS")
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Deployment assistance cancelled.")
            self.log("User cancelled deployment", "WARNING")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            self.log(f"Error during deployment: {e}", "ERROR")

def main():
    """Main entry point"""
    assistant = DeploymentAssistant()
    
    # Initialize log
    with open(assistant.deployment_log, 'w') as f:
        f.write(f"=== Deployment Log Started: {datetime.now()} ===\n\n")
    
    assistant.run_guided_deployment()

if __name__ == "__main__":
    main()
