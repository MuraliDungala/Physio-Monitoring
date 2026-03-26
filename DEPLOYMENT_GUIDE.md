# 🚀 Complete End-to-End Deployment Guide

## Project Overview

- **Backend**: Python FastAPI API Server
- **Frontend**: HTML/CSS/JavaScript Static Files
- **Database**: PostgreSQL (production)
- **Deployment Platforms**: Render/Railway (backend), Vercel/Netlify (frontend)

---

## Table of Contents

1. [Local Setup & Testing](#local-setup--testing)
2. [Database Setup](#database-setup)
3. [Backend Deployment (Render)](#backend-deployment-render)
4. [Backend Deployment (Railway)](#backend-deployment-railway)
5. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
6. [Frontend Deployment (Netlify)](#frontend-deployment-netlify)
7. [Post-Deployment Verification](#post-deployment-verification)
8. [Troubleshooting](#troubleshooting)

---

## Local Setup & Testing

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/Physio-Monitoring.git
cd Physio-Monitoring
```

### Step 2: Set Up Environment Variables

```bash
cd physio-web/backend

# Copy environment template
cp .env.example .env

# Generate a secure SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env with:
# SECRET_KEY=<your-generated-key>
# ENVIRONMENT=development
# DATABASE_URL=sqlite:///./physio_monitoring.db
```

### Step 3: Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run Locally with Docker Compose

```bash
cd ../..  # Return to project root
docker-compose up -d
```

This will start:
- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **pgAdmin**: http://localhost:5050

**Access Points:**
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- pgAdmin (DB Management): http://localhost:5050 (admin@physio.com / admin)

### Step 5: Test API

```bash
# Health check
curl http://localhost:8000/health

# API Documentation
open http://localhost:8000/docs
```

### Step 6: Stop Containers

```bash
docker-compose down
```

---

## Database Setup

### PostgreSQL Connection String Format

```
postgresql://username:password@host:port/database_name
```

### Remote Database Options

#### Option A: Render PostgreSQL
1. Go to [Render.com](https://render.com)
2. Create new PostgreSQL instance
3. Copy connection string from Render dashboard
4. Connection string example:
   ```
   postgresql://physio_user:YOUR_PASSWORD@dpg-abc123xyz.render-sydney.internal:5432/physio_monitoring_prod
   ```

#### Option B: Railway PostgreSQL
1. Go to [Railway.app](https://railway.app)
2. Create new PostgreSQL service
3. Get connection string from service variables
4. Connection string example:
   ```
   postgresql://postgres:YOUR_PASSWORD@containers.railway.app:7583/railway
   ```

### Initialize Production Database

```bash
# For Render/Railway, database tables are auto-created by SQLAlchemy
# Just ensure DATABASE_URL env variable is set
```

---

## Backend Deployment (Render)

### Step 1: Push Code to GitHub

```bash
cd ~/Desktop/Physio-Monitoring

# Initialize git if not already done
git init
git add .
git commit -m "Initial deployment setup with Docker and configs"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/Physio-Monitoring.git
git push -u origin main
```

### Step 2: Create Render Account

1. Sign up at [Render.com](https://render.com)
2. Connect GitHub account
3. Grant access to your repository

### Step 3: Deploy Backend Service

1. Click "New" → "Web Service"
2. Select your GitHub repository
3. Configure:

   ```
   Name: physio-monitoring-backend
   Branch: main
   Root Directory: physio-web/backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app:app --host 0.0.0.0 --port $PORT
   ```

4. Click "Create Web Service"

### Step 4: Set Environment Variables (Render)

In the Render dashboard for your web service:

1. Go to "Environment" tab
2. Add the following environment variables:

   ```
   ENVIRONMENT=production
   SECRET_KEY=<your-generated-key>
   DATABASE_URL=postgresql://...  (from your database)
   CORS_ORIGINS=https://your-frontend-domain.vercel.app,https://your-domain.com
   PORT=10000
   PYTHON UNBUFFERED=1
   LOG_LEVEL=info
   ```

3. Click "Save"

### Step 5: Deploy

Render will automatically deploy when you push to GitHub. Monitor the deployment in the dashboard.

**Backend URL**: Will be displayed in Render dashboard (e.g., `https://physio-monitoring-backend.onrender.com`)

---

## Backend Deployment (Railway)

### Step 1: Create Railway Account

1. Sign up at [Railway.app](https://railway.app)
2. Connect GitHub account

### Step 2: Create Backend Service

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize Railway project in root directory
cd ~/Desktop/Physio-Monitoring
railway init

# Set workspace
railway link

# Create new service
railway service add

# Configure the service to point to backend
```

### Step 3: Set Environment Variables (Railway)

In Railway dashboard:

1. Select your web service
2. Go to "Variables" tab
3. Add:

   ```
   ENVIRONMENT=production
   SECRET_KEY=<your-generated-key>
   DATABASE_URL=<your-postgres-string>
   CORS_ORIGINS=https://your-frontend-domain.vercel.app
   PYTHONUNBUFFERED=1
   PORT=8000
   ```

### Step 4: Deploy from CLI

```bash
# Navigate to backend directory
cd physio-web/backend

# Deploy
railway deploy

# Get service URL
railway open
```

**Backend URL**: Available in Railway dashboard

---

## Frontend Deployment (Vercel)

### Step 1: Create Vercel Account

1. Sign up at [Vercel.com](https://vercel.com)
2. Connect GitHub account

### Step 2: Deploy Frontend

1. Import repository: Click "New Project"
2. Select your GitHub repository
3. Configure:

   ```
   Framework Preset: Other (Static)
   Build Command: (leave blank)
   Output Directory: physio-web/frontend
   Root Directory: . (or leave recommended)
   ```

4. Click "Deploy"

### Step 3: Set Environment Variables (Vercel)

After deployment:

1. Go to Project Settings
2. Environment Variables
3. Add:

   ```
   REACT_APP_API_URL=https://your-backend-url.onrender.com
   REACT_APP_ENVIRONMENT=production
   ```

4. Go to "Deployments" → Redeploy to apply env vars

### Step 4: Update API URL in Frontend

The `config.js` file automatically detects environment variables. Ensure it loads properly by checking:

1. Go to deployed URL
2. Open Browser DevTools (F12)
3. Check Console for: "🔧 Frontend Configuration"
4. Verify API Base URL points to your backend

---

## Frontend Deployment (Netlify)

### Step 1: Create Netlify Account

1. Sign up at [Netlify.com](https://netlify.com)
2. Connect GitHub account

### Step 2: Deploy Frontend

1. Click "Add new site" → "Import an existing project"
2. Select GitHub repository
3. Configure:

   ```
   Owner: Your Account
   Branch to deploy: main
   Build command: (leave blank)
   Publish directory: physio-web/frontend
   ```

4. Click "Deploy site"

### Step 3: Set Environment Variables (Netlify)

1. Site Settings → Build & Deploy → Environment
2. Add:

   ```
   REACT_APP_API_URL=https://your-backend-url
   REACT_APP_ENVIRONMENT=production
   ```

3. Trigger redeploy

### Step 4: Configure Redirects

Netlify automatically uses `netlify.toml`. Verify it exists in root:

```toml
[[redirects]]
from = "/*"
to = "/index.html"
status = 200
```

---

## Post-Deployment Verification

### 1. Check Backend Health

```bash
# Replace with your backend URL
curl https://your-backend-url.onrender.com/health

# Expected response:
# {
#   "status": "healthy",
#   "environment": "production",
#   "version": "1.0.0",
#   "timestamp": "2024-03-26T..."
# }
```

### 2. Check API Documentation

```
https://your-backend-url.onrender.com/docs
```

### 3. Test Frontend

Open your frontend URL in browser and:

1. Check Browser Console (F12)
2. Verify "🔧 Frontend Configuration" logs correct API URL
3. Try logging in to test API connectivity
4. Test exercise detection with camera

### 4. Test WebSocket Connection

Frontend will automatically establish WebSocket connection when you start an exercise session.

---

## Troubleshooting

### Problem: CORS Errors

**Symptom**: Frontend can't reach backend API

**Solution**:
1. Check Backend CORS_ORIGINS env var includes frontend domain
2. Update and redeploy backend
3. Clear browser cache (Ctrl+Shift+Delete)

**Example fix for Render:**
```
CORS_ORIGINS=https://your-domain-123.vercel.app,https://your-domain.com
```

### Problem: 502 Bad Gateway

**Symptom**: Backend returning 502 error

**Solution**:
1. Check backend logs in Render/Railway dashboard
2. Verify DATABASE_URL is correct
3. Check SECRET_KEY is set
4. Restart service

### Problem: Database Connection Error

**Symptom**: "could not connect to server"

**Solution**:
1. Verify DATABASE_URL format is correct
2. Verify database credentials
3. Allow IP whitelist if using external DB
4. Test connection string locally first

### Problem: Frontend Can't Find Backend

**Symptom**: API requests return 404 or connection refused

**Solution**:
1. Verify REACT_APP_API_URL env var is set correctly
2. Redeploy frontend after setting env vars
3. Check browser console for actual API URL being used
4. Verify backend is running (check health endpoint)

### Problem: MediaPipe Not Loading

**Symptom**: "MediaPipe not available" in logs

**Solution**:
1. This is expected in server environments without GPU
2. System uses fallback detection mode
3. For production ML inference, upload pre-processed video
4. Frontend will still work for real-time pose detection

---

## Monitoring & Maintenance

### Enable Monitoring (Render)

1. Go to service settings
2. Enable email alerts for deployments
3. Set up uptime monitoring

### View Logs

**Render:**
```bash
# In Render dashboard, click "Logs" tab for real-time logs
```

**Railway:**
```bash
railway logs -f  # Follow logs
```

### Update Environment Variables

**Render:**
- Dashboard → Service → Environment → Update value → Save

**Railway:**
- Dashboard → Variables → Edit value → Save

**Vercel/Netlify:**
- Settings → Environment Variables → Edit → Redeploy

---

## Final Checklist

- [ ] GitHub repository created and pushed
- [ ] Backend deployed to Render/Railway
- [ ] Database created and connected
- [ ] Environment variables set on backend
- [ ] Frontend deployed to Vercel/Netlify
- [ ] Frontend environment variables set
- [ ] Backend health endpoint responding
- [ ] API documentation accessible
- [ ] Frontend loads without CORS errors
- [ ] Login/registration works
- [ ] Exercise detection works in production
- [ ] WebSocket connection established

---

## Support & Additional Resources

- **Render Docs**: https://render.com/docs
- **Railway Docs**: https://docs.railway.app
- **Vercel Docs**: https://vercel.com/docs
- **Netlify Docs**: https://docs.netlify.com
- **FastAPI in Production**: https://fastapi.tiangolo.com/deployment/
- **Your Backend API Docs**: [Backend URL]/docs

---

## Next Steps

1. **Domain Setup**: Use your custom domain with Vercel/Netlify DNS
2. **SSL Certificate**: Automatically handled by Render/Railway/Vercel/Netlify
3. **Email Notifications**: Set up GitHub workflow notifications
4. **Scaling**: Monitor performance and scale as needed
5. **CI/CD**: Set up automated tests in GitHub Actions

