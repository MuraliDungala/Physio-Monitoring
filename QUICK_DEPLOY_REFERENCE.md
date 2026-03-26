# 🚀 QUICK DEPLOYMENT - Copy & Paste Commands

## Your Deployment Info

**Fill in these once you start deployment:**

```
Render Backend URL:        https://___________________________
Vercel Frontend URL:       https://___________________________
SECRET_KEY:                ___________________________________
DATABASE_URL:              postgresql://______________________
```

---

## Step 1: GitHub Push (Run in Terminal)

```powershell
cd c:\Users\Murali\Desktop\Physio-Monitoring

git add .
git commit -m "Production deployment configuration"
git push origin main
```

---

## Step 2: Create Database (One-time)

Choose one option:

### Option A: Render PostgreSQL (Easiest)

1. Go to: https://dashboard.render.com
2. Click: "New" → "PostgreSQL"
3. Name: `physio-db`
4. Region: Choose closest
5. Save the connection string

### Option B: Railway PostgreSQL

1. Go to: https://dashboard.railway.app
2. New Project → Add PostgreSQL
3. Copy connection string

---

## Step 3: Get SECRET_KEY

In any terminal (or Generate Online):

```python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Or use online generator: https://generate-secret-key.vercel.app/

---

## Step 4: Backend Deployment - Render

### Configuration

| Setting | Value |
|---------|-------|
| URL | https://dashboard.render.com |
| New | Web Service |
| GitHub Repo | Physio-Monitoring |
| Branch | main |
| Root Directory | `physio-web/backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app:app --host 0.0.0.0 --port $PORT` |

### Environment Variables

Copy these exactly:

```
ENVIRONMENT=production
SECRET_KEY=<your-generated-key>
DATABASE_URL=<postgresql-url>
CORS_ORIGINS=https://your-vercel-domain.vercel.app
PYTHONUNBUFFERED=1
LOG_LEVEL=info
```

### Timeline

- Click "Create Web Service"
- ⏳ 2-3 minutes for deployment
- ✅ Shows "Live" when ready
- 📋 Copy the service URL

---

## Step 5: Test Backend

Once "Live":

```bash
# Test health
curl https://your-backend-url/health

# Check API docs
Open in browser: https://your-backend-url/docs

# Expected:
# Health returns: {"status":"healthy",...}
# Docs shows: Swagger UI with all endpoints
```

---

## Step 6: Frontend Deployment - Vercel

### Configuration

| Setting | Value |
|---------|-------|
| URL | https://vercel.com/dashboard |
| New | Project |
| GitHub Repo | Physio-Monitoring |
| Framework | Other (Static) |
| Root Directory | `.` |
| Output Directory | `physio-web/frontend` |
| Build Command | (leave blank) |

### Environment Variables

```
REACT_APP_API_URL=https://your-backend-url.onrender.com
REACT_APP_ENVIRONMENT=production
```

### Timeline

- Click "Deploy"
- ⏳ 1-2 minutes for deployment
- ✅ Shows deployment complete
- 📋 Copy the domain

---

## Step 7: Connect Frontend to Backend

### Go Back to Render

1. Service → Environment Variables
2. Update CORS_ORIGINS: `https://your-vercel-domain.vercel.app`
3. Save → Auto-redeploys (~2 min)

### Go Back to Vercel

1. Settings → Environment Variables
2. Add/Update API URL
3. Deployments → Redeploy latest
4. Wait for green checkmark

---

## Step 8: Final Verification

### Test Health (Backend OK)

```bash
curl https://your-backend.onrender.com/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "environment": "production",
  "version": "1.0.0",
  "timestamp": "2024-03-26T..."
}
```

### Test Frontend (Open in Browser)

```
https://your-app.vercel.app
```

**Expected:**
- Page loads without errors
- Logo and interface visible
- F12 Console shows: "🔧 Frontend Configuration"

### Test Backend API Docs

```
https://your-backend.onrender.com/docs
```

**Expected:**
- Swagger UI loads
- All API endpoints listed

---

## Quick Troubleshooting

### CORS Error?
✅ Solution: Set `CORS_ORIGINS` on Render to match Vercel domain exactly

### API Not Responding?
✅ Solution: Redeploy both frontend and backend after setting environment variables

### 502 Error?
✅ Solution: Check Render logs, verify `DATABASE_URL` and `SECRET_KEY`

### WebSocket Won't Connect?
✅ Solution: Verify backend health endpoint works first

---

## Files Ready for Deployment

```
✅ backend/config.py
✅ backend/.env.production
✅ backend/Dockerfile
✅ frontend/config.js
✅ frontend/.env.production
✅ render.yaml
✅ vercel.json
✅ .gitignore
✅ docker-compose.yml
```

---

## Required Accounts

```
✅ GitHub - https://github.com (for code repo)
✅ Render - https://render.com (backend hosting)
✅ Vercel - https://vercel.com (frontend hosting)
✅ PostgreSQL - Render or Railway (database)
```

---

## Important URLs

During deployment, you'll need:

| Purpose | URL |
|---------|-----|
| GitHub | https://github.com/YOUR_USERNAME/Physio-Monitoring |
| Render Dashboard | https://dashboard.render.com |
| Vercel Dashboard | https://vercel.com/dashboard |
| Render Docs | https://render.com/docs |
| Vercel Docs | https://vercel.com/docs |

---

## Total Time Estimate

- GitHub Push: **5 min**
- Render Deployment: **5 min** (+ 2-3 min wait)
- Vercel Deployment: **3 min** (+ 1-2 min wait)
- Configuration: **10 min**
- Verification: **5 min**

**Total: ~45 minutes**

---

## Success Criteria

You'll know deployment is successful when:

✅ `curl https://your-backend/health` returns HTTP 200  
✅ Frontend loads at `https://your-app.vercel.app`  
✅ Browser console shows API configuration  
✅ Login works end-to-end  
✅ WebSocket connects (websocket.readyState === 1)  
✅ No CORS errors in console  

---

## After Deployment (Optional)

1. **Custom Domain** (both platforms support)
2. **DNS Configuration** (point domain to Render/Vercel)
3. **Monitoring Alerts** (set up in dashboards)
4. **Database Backups** (enable in Render)
5. **Auto Deployments** (already configured via GitHub)

---

## Still Need Help?

📖 Read: `PRODUCTION_DEPLOYMENT_CHECKLIST.md` (step-by-step with screenshots info)
🔧 Reference: `DEPLOYMENT_GUIDE.md` (detailed technical guide)
❓ FAQ: `DEPLOYMENT_SUMMARY.md` (common questions)

---

**Good luck! 🚀**

Your production deployment is minutes away!
