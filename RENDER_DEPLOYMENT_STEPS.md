# 🚀 Backend Deployment Guide - Physio-Monitoring

**Target**: Deploy to Render  
**Time**: ~10 minutes  
**Status**: Ready to deploy

---

## ✅ Pre-Deployment Checklist

- ✅ `requirements.txt` - All dependencies listed
- ✅ `runtime.txt` - Python 3.11.9 specified
- ✅ `Procfile` - Start command defined
- ✅ `render.yaml` - Render configuration ready
- ✅ `.env.production` - Production env template
- ✅ `app.py` - FastAPI main application
- ✅ CORS already configured

---

## 📝 Step 1: Create Render Account (2 min)

1. Go to **https://render.com**
2. Sign up with GitHub (easiest option)
   - Or use Google/Email
3. Authorize Render to access your GitHub account

---

## 🔑 Step 2: Generate Secure SECRET_KEY (1 min)

Run this in PowerShell to generate a secure key:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Example output:**
```
kJ_1a2bC3d4eF5g6h7i8jK9l0mNoPqRsTuV
```

**Copy this to clipboard** - you'll need it shortly.

---

## 📦 Step 3: Deploy to Render (5 min)

### Option A: Deploy from GitHub (Recommended)

1. **Go to Render Dashboard**: https://dashboard.render.com

2. **Click "New +"** → **"Web Service"**

3. **Connect Repository**:
   - Click "Build and deploy from a Git repository"
   - Select "GitHub"
   - Find: `Physio-Monitoring` repository
   - Click "Connect"

4. **Fill in Service Details**:
   ```
   Name                 : physio-monitoring-backend
   Region               : Select closest to you (e.g., US-East)
   Build Command        : pip install -r requirements.txt
   Start Command        : uvicorn app:app --host 0.0.0.0 --port $PORT
   Environment          : Python 3
   ```

5. **Scroll Down** → Check "Root Directory"
   - Set to: `physio-web/backend`

6. **Add Environment Variables** (click "Advanced"):
   ```
   Key                  | Value
   ---|---
   ENVIRONMENT          | production
   SECRET_KEY           | [Paste the key you generated above]
   DATABASE_URL         | sqlite:///./physio_monitoring.db
   CORS_ORIGINS         | *
   ```

   **For production with PostgreSQL** (optional but recommended):
   ```
   DATABASE_URL         | postgresql://user:password@your-db-host:5432/physio_prod
   ```

7. **Instance Type**: 
   - Select "Free" tier (perfect for testing)
   - Or upgrade to "Starter Plus" ($7/month) for production

8. **Click "Create Web Service"**

---

## ⏳ Step 4: Wait for Deployment (3-5 min)

Watch the deployment progress in the Render dashboard:

1. **Building** - `pip install` and setup
2. **Deploying** - Starting the application  
3. **Live** - Your backend is ready! ✅

**Look for**: 
```
✓ Build successful
✓ Service is live at: https://physio-monitoring-backend.onrender.com
```

---

## ✅ Step 5: Verify Backend is Working

### Test 1: Health Check
```bash
curl https://physio-monitoring-backend.onrender.com/health
```

**Expected Response:**
```json
{
    "status": "healthy",
    "environment": "production",
    "version": "1.0.0",
    "timestamp": "2026-03-26T..."
}
```

### Test 2: Get Exercises
```bash
curl https://physio-monitoring-backend.onrender.com/exercises
```

Should return list of exercises (or empty if DB not initialized)

### Test 3: Full Registration Test (in browser DevTools)
```javascript
fetch('https://physio-monitoring-backend.onrender.com/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: 'testuser123',
        email: 'test@example.com',
        full_name: 'Test User',
        password: 'TestPass123!'
    })
})
.then(r => r.json())
.then(d => console.log('Response:', d))
```

---

## 🔗 Step 6: Update Frontend Config

Now that your backend is deployed, update your frontend to use it:

### Edit: `physio-web/frontend/index.html`

Add right after `<head>` tag:

```html
<head>
    <!-- ... other head content ... -->
    
    <!-- Configure Backend API URL -->
    <script>
        window.API_BASE_URL = 'https://physio-monitoring-backend.onrender.com';
        console.log('✅ Backend configured:', window.API_BASE_URL);
    </script>
    
    <!-- ... rest of head ... -->
</head>
```

**Or set in Vercel environment variables:**
1. Vercel Dashboard → Project Settings
2. Environment Variables
3. Add: `API_BASE_URL` = `https://physio-monitoring-backend.onrender.com`

---

## 🧪 Step 7: Test Full Flow

1. Open your Vercel frontend
2. Click "Register"
3. Fill in details:
   ```
   Username: testuser_001
   Email: testuser001@gmail.com
   Full Name: Test User
   Password: TestPass123!
   ```
4. Expected: ✅ Registration successful!
5. Try logging in with same credentials

---

## 🐛 Troubleshooting

### Problem: "Connection error" when registering

**Check**:
```javascript
// In browser console:
console.log(window.API_BASE_URL);
// Should show: https://physio-monitoring-backend.onrender.com
```

**Fix**: Make sure you updated frontend config with correct backend URL

### Problem: Backend deployment failed

**Check logs** in Render dashboard:
1. Select your service
2. Click "Logs" tab
3. Look for error messages

**Common errors**:
```
ModuleNotFoundError: No module named 'fastapi'
→ Solution: pip install -r requirements.txt ran successfully?

ImportError: Cannot import name 'app'
→ Solution: Check app.py exists and is in root backend folder

Port already in use
→ Solution: Render handles this, shouldn't happen
```

### Problem: Database not working

**For SQLite** (development):
- Built-in, no setup needed
- Data stored: `physio_monitoring.db`

**For PostgreSQL** (production - recommended):
1. Add PostgreSQL to Render service
2. Render provides `DATABASE_URL` automatically
3. Set in environment variables

### Problem: CORS errors

**Fix in `config.py`**:
```python
CORS_ORIGINS = [
    "https://your-vercel-frontend.vercel.app",
    "http://localhost:3000",  # for local testing
]
```

---

## 📊 Getting Your Backend URL

After successful deployment, Render shows:

```
Service Dashboard
├─ Name: physio-monitoring-backend
├─ Status: ✅ Live
├─ URL: https://physio-monitoring-backend.onrender.com
├─ Region: US-East
└─ Plan: Free
```

**Your Backend URL**: `https://physio-monitoring-backend.onrender.com`

---

## 🔐 Production Security Checklist

Before going live to public:

- ✅ Change `SECRET_KEY` to a strong random value
- ✅ Set `ENVIRONMENT=production`
- ✅ Use PostgreSQL (not SQLite) for database
- ✅ Restrict `CORS_ORIGINS` to only your frontend domain
- ✅ Enable HTTPS (Render does this by default)
- ✅ Set up database backups
- ✅ Monitor logs for errors

---

## 📈 Next Steps After Deployment

1. **Initialize Database**:
   ```bash
   # SSH into Render or use CLI:
   python init_db.py
   python populate_exercises.py
   ```

2. **Set Up Monitoring**:
   - Enable Render alerts for failures
   - Monitor response times

3. **Configure Auto-Restart**:
   - Render keeps services alive automatically
   - No additional setup needed

4. **Scale if Needed**:
   - Start on Free tier (perfect for testing)
   - Upgrade to Starter ($7/month) for production

---

## ✨ Backend is Now Live!

🎉 **Congratulations!**

Your backend is deployed and accessible globally:
- ✅ **API URL**: `https://physio-monitoring-backend.onrender.com`
- ✅ **Health Check**: `https://physio-monitoring-backend.onrender.com/health`
- ✅ **Register Endpoint**: `POST /register`
- ✅ **Login Endpoint**: `POST /token`

---

## 📞 Support

**Issues?** Check:
1. Render dashboard → Logs
2. Backend requirements.txt all installed
3. Frontend `window.API_BASE_URL` correctly set
4. CORS enabled in backend

---

**Status**: ✅ Ready to Deploy  
**Time**: ~10 minutes  
**Difficulty**: Easy  

**Last Updated**: March 26, 2026
