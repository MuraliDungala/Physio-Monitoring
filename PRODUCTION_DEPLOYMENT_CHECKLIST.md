# 🚀 PRODUCTION DEPLOYMENT CHECKLIST - RENDER & VERCEL

**Status**: Ready to Deploy  
**Platform**: Render.com (Backend) + Vercel (Frontend)  
**Estimated Time**: 30-45 minutes  
**Difficulty**: Easy (mostly clicking)

---

## ✅ PRE-DEPLOYMENT (Next 5 minutes)

### Accounts Needed
- [ ] GitHub Account (https://github.com)
- [ ] Render Account (https://render.com) 
- [ ] Vercel Account (https://vercel.com)

### Files Ready
- [ ] backend/config.py exists
- [ ] backend/Dockerfile exists  
- [ ] frontend/config.js exists
- [ ] .gitignore exists
- [ ] docker-compose.yml exists

---

## 📤 STEP 1: Push to GitHub (5 minutes)

> **What**: Upload your code to GitHub so Render/Vercel can access it

### 1.1 Open Terminal in Project Root

```
c:\Users\Murali\Desktop\Physio-Monitoring>
```

### 1.2 Stage Changes

```powershell
git add .
```

### 1.3 Commit Changes

```powershell
git commit -m "Production deployment configuration"
```

### 1.4 Push to GitHub

```powershell
git push origin main
```

### 1.5 Verify Push

Go to GitHub.com → Your Repository → Should see recent commits

✅ **Checkpoint**: Code is now on GitHub

---

## 🔧 STEP 2: Deploy Backend to Render (5 minutes)

> **What**: Deploy FastAPI backend to Render.com

### 2.1 Go to Render Dashboard

Open: https://dashboard.render.com

Sign in or create account

### 2.2 Create Web Service

1. Click **"New"** (top right)
2. Select **"Web Service"**

### 2.3 Connect GitHub

1. Under "Public Git repository", paste your repo URL:
   ```
   https://github.com/YOUR_USERNAME/Physio-Monitoring.git
   ```

2. Click **"Connect"**

3. Grant GitHub permissions if asked

### 2.4 Configure Service

Fill in these fields:

| Field | Value |
|-------|-------|
| **Name** | `physio-monitoring-backend` |
| **Branch** | `main` |
| **Runtime** | `Python 3` |
| **Root Directory** | `physio-web/backend` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app:app --host 0.0.0.0 --port $PORT` |
| **Plan** | `Free` (or Starter if needed) |

### 2.5 Add Environment Variables

Click **"Add Environment Variable"** for each:

```
ENVIRONMENT           = production
SECRET_KEY            = [Copy from DEPLOYMENT_SECRETS.json]
DATABASE_URL          = postgresql://user:pass@host:5432/db
CORS_ORIGINS          = https://YOUR-VERCEL-DOMAIN.vercel.app
PYTHONUNBUFFERED      = 1
LOG_LEVEL             = info
```

⚠️ **Where to get SECRET_KEY:**
- Open file: `DEPLOYMENT_SECRETS.json`
- Copy value for `backend.SECRET_KEY`

⚠️ **Where to get DATABASE_URL:**
- Create PostgreSQL database on Render first
- Or use your own database connection string
- Format: `postgresql://username:password@host:5432/database`

### 2.6 Create Service

Click **"Create Web Service"**

⏳ **Wait**: 2-3 minutes for deployment

### 2.7 Get Backend URL

Once it says "Live" in green:
1. Copy the URL (top of page)
2. Example: `https://physio-monitoring-backend.onrender.com`
3. **Save this URL** - you'll need it for frontend

✅ **Checkpoint**: Backend is deployed!  
✅ **Test**: Visit `https://your-backend-url/health` (should return JSON)

---

## 🌐 STEP 3: Deploy Frontend to Vercel (3 minutes)

> **What**: Deploy HTML/CSS/JavaScript frontend to Vercel

### 3.1 Go to Vercel Dashboard

Open: https://vercel.com/dashboard

Sign in or create account

### 3.2 Import Project

1. Click **"Add New..."** (top)
2. Select **"Project"**
3. Click **"Continue with GitHub"**
4. Select your Physio-Monitoring repository

### 3.3 Configure Project

Fill in these fields:

| Field | Value |
|-------|-------|
| **Framework** | `Other (Static)` |
| **Build Command** | (leave blank) |
| **Output Directory** | `physio-web/frontend` |
| **Root Directory** | `.` |

### 3.4 Deploy

1. Click **"Deploy"**
2. ⏳ Wait 1-2 minutes

### 3.5 Get Frontend URL

Once deployment completes:
1. Copy the domain (shown at top)
2. Example: `https://physio-app-123.vercel.app`
3. **Save this URL**

✅ **Checkpoint**: Frontend is deployed!

---

## 🔗 STEP 4: Connect Frontend to Backend (5 minutes)

> **What**: Tell frontend where to find backend API

### 4.1 Update CORS on Render

1. Go to Render Dashboard
2. Select your backend service
3. Click **"Environment"** tab
4. Find **CORS_ORIGINS**
5. Update to: `https://YOUR-VERCEL-DOMAIN.vercel.app`
6. Click **"Save"**

⏳ Backend automatically redeploys (~2 minutes)

### 4.2 Set Frontend API URL

1. Go to Vercel Dashboard
2. Click your project (physio-app-123)
3. Go to **"Settings"** → **"Environment Variables"**
4. Click **"Add New"** for each variable:

| Key | Value |
|-----|-------|
| `REACT_APP_API_URL` | `https://your-backend-url.onrender.com` |
| `REACT_APP_ENVIRONMENT` | `production` |

5. Click **"Save"**

### 4.3 Redeploy Frontend

1. Go to **"Deployments"** tab
2. Find the latest deployment
3. Click the **⋮ (three dots)** next to it
4. Click **"Redeploy"**

⏳ Wait 1-2 minutes for redeployment

✅ **Checkpoint**: Frontend and backend are connected!

---

## ✨ STEP 5: Verify Everything Works (10 minutes)

### 5.1 Test Health Endpoint

In browser, visit:
```
https://your-backend.onrender.com/health
```

**Expected**: Page shows JSON like:
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0"
}
```

❌ **If not working**: Check Render logs (Dashboard → Service → Logs)

### 5.2 Check API Documentation

In browser, visit:
```
https://your-backend.onrender.com/docs
```

**Expected**: Swagger UI loads with all API endpoints

❌ **If not working**: Backend deployment failed

### 5.3 Open Frontend

In browser, visit:
```
https://your-vercel-domain.vercel.app
```

**Expected**: PhysioMonitor app loads

❌ **If not working**: Check browser console (F12)

### 5.4 Check Configuration Logs

1. Open frontend URL
2. Press **F12** (Developer Tools)
3. Click **Console** tab
4. Look for: `🔧 Frontend Configuration`
5. Verify API URL matches your backend

**Example output:**
```
🔧 Frontend Configuration:
   API Base URL: https://your-backend.onrender.com
   Environment: production
   Hostname: your-vercel-domain.vercel.app
```

❌ **If API URL is wrong**: Environment variable not set correctly

### 5.5 Test Login

1. Click "Login"
2. Create test account or use existing credentials
3. Should log in successfully

❌ **If CORS error**: Update CORS_ORIGINS and redeploy backend

✅ **Checkpoint**: All systems working!

---

## 🎉 STEP 6: Final Verification (Optional but Recommended)

### 6.1 Test Exercise Features (if camera available)

1. Log in to app
2. Go to "Exercises"
3. Start "Shoulder Press"
4. Grant camera permission
5. Should see pose detection live
6. Real-time rep counting should work

### 6.2 Test Mobile Responsiveness

1. On frontend, press F12
2. Click device icon (top left of developer tools)
3. Select "iPhone 12 Pro"
4. App should be responsive

### 6.3 Monitor Performance

1. Render Dashboard → Service → Metrics
   - Check CPU and Memory usage
   - Should be green

2. Vercel Dashboard → Project → Analytics
   - Check performance metrics

---

## ❌ TROUBLESHOOTING

### Problem: CORS Error in Frontend

**Error in Console**: "Access to XMLHttpRequest blocked by CORS"

**Solution**:
1. Go to Render Dashboard
2. Select backend service
3. Environment → CORS_ORIGINS
4. Add your Vercel domain exactly: `https://YOUR-DOMAIN.vercel.app`
5. Save and wait 2 minutes for redeployment
6. Refresh frontend browser (Ctrl+Shift+R for hard refresh)

### Problem: 502 Bad Gateway on Backend

**Error**: Backend returns 502

**Solution**:
1. Check Render Dashboard → Service → Logs
2. Look for error messages
3. Common issues:
   - DATABASE_URL is invalid → Fix and save
   - SECRET_KEY missing → Add and save
   - Port configuration → Should use $PORT env var
4. Restart service: Click button in dashboard
5. Wait 2-3 minutes

### Problem: API Not Responding

**Error**: Frontend can't reach backend

**Solution**:
1. Verify backend URL in frontend env vars
2. Test backend health: `curl https://your-backend/health`
3. If health fails:
   - Check backend logs in Render
   - Restart backend service
   - Verify DATABASE_URL is accessible
4. If health passes but frontend still fails:
   - Check CORS_ORIGINS includes frontend domain
   - Refresh frontend (Ctrl+Shift+R)
   - Clear browser cache

### Problem: Database Connection Failed

**Error**: "could not connect to server"

**Solution**:
1. Verify DATABASE_URL format: 
   - Wrong: `postgres://...` (old syntax)
   - Right: `postgresql://...` (new syntax)
2. Test connection locally first
3. Verify database is actually running
4. Check username/password are correct
5. Ensure port is 5432 (default)

### Problem: WebSocket Connection Failed

**Error**: WebSocket connection won't establish

**Solution**:
1. Must be HTTPS (Render/Vercel both use HTTPS automatically)
2. Verify backend is responding to health endpoint
3. Check browser console for specific error
4. Ensure CORS_ORIGINS is correctly set

---

## 📋 DEPLOYMENT SUMMARY

Once all steps complete, you should have:

| Component | Status | URL |
|-----------|--------|-----|
| **Backend API** | ✅ Live | `https://your-backend.onrender.com` |
| **Frontend App** | ✅ Live | `https://your-app.vercel.app` |
| **Database** | ✅ Connected | `postgresql://host:5432/...` |
| **SSL/TLS** | ✅ Automatic | All HTTPS |

---

## 📚 Additional Resources

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **FastAPI Deployment**: https://fastapi.tiangolo.com/deployment/
- **Your API Docs**: `https://your-backend.onrender.com/docs`

---

## 🚀 You're Live!

Your production deployment is complete!

**Monitor your services:**
- Render Dashboard: https://dashboard.render.com
- Vercel Dashboard: https://vercel.com/dashboard

**Next steps (optional):**
1. Set up custom domain (both platforms support this)
2. Enable monitoring alerts
3. Set up backups for database
4. Configure CI/CD for automatic deployments
5. Add analytics/monitoring

---

**Deployment Date**: _______________  
**Backend URL**: _______________  
**Frontend URL**: _______________  
**Database Host**: _______________  

✅ **DEPLOYMENT SUCCESSFUL!** 🎉
