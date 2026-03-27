# Backend Deployment Guide - Production Ready

## Overview

Your Physio-Monitoring frontend is deployed on Vercel, but the backend is still running locally on `localhost:8000`. This is why you're seeing:
- ❌ "Connection error"
- ❌ "Username already registered" (even for new users)

**Root Cause**: The frontend cannot reach a backend running on your local machine.

---

## Solution: Deploy Backend to a Production Server

Choose one of the recommended options below:

### 1️⃣ **RECOMMENDED: Render (Free tier available)**

#### Step 1: Prepare Backend Files

```bash
cd c:\Users\Murali\Desktop\Physio-Monitoring\physio-web\backend
```

Ensure you have:
- ✅ `requirements.txt` (all dependencies)
- ✅ `app.py` (main FastAPI app)
- ✅ `auth.py` (authentication)
- ✅ `database.py` (database setup)
- ✅ `models.py` (Pydantic models)
- ✅ `.env` (environment variables) - **DO NOT PUSH TO GIT**

#### Step 2: Create `.env.production`

```bash
cd c:\Users\Murali\Desktop\Physio-Monitoring\physio-web\backend
cp .env .env.production
```

Edit `.env.production`:
```
SECRET_KEY=your_super_secret_key_change_this_in_production
DATABASE_URL=postgresql://user:password@your-db-host/physio_prod
ENVIRONMENT=production
CORS_ORIGINS=["https://your-vercel-frontend.vercel.app"]
DEBUG=False
```

#### Step 3: Create `Procfile` (if not exists)

```bash
echo "web: uvicorn app:app --host 0.0.0.0 --port \$PORT" > Procfile
```

#### Step 4: Deploy to Render

1. Go to https://render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub/build from URL
4. Fill in details:
   - **Name**: `physio-monitoring-backend`
   - **Root Directory**: `physio-web/backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port 8000`
   - **Environment**: Add from `.env.production`
5. Choose **Free** tier (good for testing)
6. Click **"Deploy"**

**Wait 5-10 minutes for deployment...**

After deployment, you'll get a URL like:
```
https://physio-monitoring-backend.onrender.com
```

---

### 2️⃣ **Railway (Alternative)**

1. Go to https://railway.app
2. Click **"New Project"** → **"Deploy from GitHub"**
3. Select your repository
4. Set **Service Root Directory**: `physio-web/backend`
5. Configure environment variables:
   ```
   ENVIRONMENT=production
   SECRET_KEY=your_secret_key
   DATABASE_URL=your_db_url
   ```
6. Deploy

Get your Railway URL (e.g., `https://physio-backend-prod.railway.app`)

---

### 3️⃣ **Fly.io (Alternative)**

```bash
# Install Fly CLI
# Then:
fly auth login
fly launch --name physio-monitoring-backend

# Set environment:
fly secrets set SECRET_KEY=your_secret_key
fly secrets set ENVIRONMENT=production

# Deploy:
fly deploy
```

---

## Step 5: Update Frontend to Use Deployed Backend

### Option A: Add Config Script in `index.html`

**Before `<script src="script.js">`, add:**

```html
<head>
    <!-- ... other head content ... -->
    
    <!-- Configure API Base URL for production -->
    <script>
        // Set backend API URL
        // For development: comment out (will auto-detect localhost:8000)
        // For production: set to your deployed backend URL
        
        if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
            // Running on Vercel or deployed app - use production backend
            window.API_BASE_URL = 'https://physio-monitoring-backend.onrender.com';
            console.log('✅ Production Mode: Using deployed backend');
        } else {
            // Development mode - auto-detect localhost:8000
            console.log('✅ Development Mode: Using localhost backend');
        }
    </script>
    
    <!-- ... rest of head ... -->
</head>
```

### Option B: Environment Variable in Vercel

1. Go to Vercel Dashboard → Settings → Environment Variables
2. Add:
   - **Name**: `API_BASE_URL`
   - **Value**: `https://physio-monitoring-backend.onrender.com`
   - **Environments**: Production, Preview, Development

3. In `public/index.html` or as inline script:
```javascript
window.API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
```

---

## Step 6: Enable CORS in Backend

**Check**: Backend already has CORS enabled in `app.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### For Production, Restrict CORS:

```python
cors_origins = [
    "https://your-vercel-frontend.vercel.app",
    "http://localhost:3000",  # For local testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Step 7: Test Registration

1. **Open Vercel Frontend**
2. **Click "Register"**
3. Try to register a new user with:
   - Username: `testuser123`
   - Email: `test@example.com`
   - Password: `testpass123`

✅ Should work now!

---

## Step 8: Database Setup

### For Production, Use PostgreSQL (NOT SQLite)

#### Deploy PostgreSQL:

- **Render**: Includes free PostgreSQL database
- **Railway**: PostgreSQL add-on available
- **Fly.io**: PostgreSQL service available

#### Update `.env.production`:

```
DATABASE_URL=postgresql://username:password@database-host:5432/physio_prod
SQLALCHEMY_DATABASE_URL=postgresql://username:password@database-host:5432/physio_prod
```

#### Initialize Database:

```bash
# After deploying, run init script in Render CLI or SSH:
cd backend
python init_db.py
```

---

## Troubleshooting

### Problem 1: "Connection error" after deployment

```yaml
Cause: API_BASE_URL not set correctly
Fix:
  1. Check browser DevTools → Network → check request URLs
  2. Verify window.API_BASE_URL is set in console: window.API_BASE_URL
  3. Make sure CORS headers are present in response
```

### Problem 2: "Username already registered" for new users

```yaml
Cause: Database query logic issue or connection problem
Fix:
  1. Check backend logs on Render/Railway
  2. Verify database is connected: SELECT * FROM users;
  3. Try clearing browser storage: localStorage.clear()
```

### Problem 3: CORS errors

```yaml
Error: "Access to XMLHttpRequest blocked by CORS policy"
Fix:
  1. Verify CORS middleware is enabled in app.py
  2. Check allow_origins includes frontend domain
  3. Restart backend service after changes
```

### Problem 4: Database connection fails on deployment

```yaml
Cause: DATABASE_URL not set or invalid
Fix:
  1. Verify DATABASE_URL in production environment
  2. Test connection: psql $DATABASE_URL
  3. Run migration scripts
```

---

## Production Checklist

Before going live:

- ✅ Backend deployed to Render/Railway/Fly.io
- ✅ Frontend `API_BASE_URL` configured correctly
- ✅ CORS headers include frontend domain
- ✅ PostgreSQL database connected
- ✅ SECRET_KEY changed from default
- ✅ ENVIRONMENT=production in .env
- ✅ DEBUG=False in production
- ✅ Test registration with new user
- ✅ Test login with registered user
- ✅ Check error logs for any issues
- ✅ Voice Assistant UI only shows on exercise/settings pages

---

## Quick Reference: URLs After Deployment

| Component | URL |
|-----------|-----|
| Frontend (Vercel) | `https://your-app.vercel.app` |
| Backend (Render) | `https://physio-monitoring-backend.onrender.com` |
| Health Check | `https://physio-monitoring-backend.onrender.com/health` |
| Register API | `POST https://physio-monitoring-backend.onrender.com/register` |
| Login API | `POST https://physio-monitoring-backend.onrender.com/token` |

---

## Support

If issues persist:

1. **Check Backend Logs** (Render Dashboard):
   - Recent → select service → "Logs" tab
   
2. **Test API Directly**:
   ```bash
   curl https://physio-monitoring-backend.onrender.com/health
   ```

3. **Browser Console** (F12):
   - Network tab → check request/response
   - Console → check JavaScript errors

---

**Last Updated**: March 2026
**Status**: Production Ready
