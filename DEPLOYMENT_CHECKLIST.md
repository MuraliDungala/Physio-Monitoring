# ✅ Backend Deployment Checklist

**Status**: Ready to Deploy  
**Time**: 10 minutes  
**Difficulty**: Easy

---

## 📋 Pre-Deployment Verification

### Files Ready ✅
- [x] `requirements.txt` - All dependencies 
- [x] `runtime.txt` - Python 3.11.9
- [x] `Procfile` - Created ✅
- [x] `render.yaml` - Created ✅
- [x] `.env.production` - Template provided
- [x] `app.py` - FastAPI main app
- [x] `config.py` - Settings configured
- [x] CORS middleware enabled

### Configuration Ready ✅
- [x] Database connection configured
- [x] Auth endpoints working
- [x] Health check endpoint available
- [x] Static files mounted
- [x] WebSocket support ready

---

## 🚀 Quick Deployment Steps

### 1️⃣ Generate SECRET_KEY (Copy-Paste)
```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
**Save this value** - you'll need it in Render

### 2️⃣ Go to Render
- Visit: https://render.com
- Sign in with GitHub
- Click: **"New +"** → **"Web Service"**

### 3️⃣ Connect Repository
- Click: **"Build and deploy from Git repository"**
- Select: **"GitHub"**
- Choose: **"Physio-Monitoring"** repo
- Click: **"Connect"**

### 4️⃣ Configure Service
```
Name:              physio-monitoring-backend
Root Directory:    physio-web/backend
Build Command:     pip install -r requirements.txt
Start Command:     uvicorn app:app --host 0.0.0.0 --port $PORT
Environment:       Python 3
```

### 5️⃣ Add Environment Variables
- Click "Advanced"
- Add:
  ```
  ENVIRONMENT     = production
  SECRET_KEY      = [Paste from Step 1️⃣]
  DATABASE_URL    = sqlite:///./physio_monitoring.db
  CORS_ORIGINS    = *
  ```

### 6️⃣ Create Service
- Instance Type: **Free** (for testing)
- Click: **"Create Web Service"**
- Wait: 3-5 minutes ⏳

### 7️⃣ Test Backend
Once live, test:
```bash
curl https://physio-monitoring-backend.onrender.com/health
```

Should return:
```json
{"status": "healthy", "environment": "production"}
```

### 8️⃣ Update Frontend
Edit `physio-web/frontend/index.html`:
```html
<script>
    window.API_BASE_URL = 'https://physio-monitoring-backend.onrender.com';
</script>
```

### 9️⃣ Test Full Registration
1. Open your Vercel frontend
2. Click "Register"
3. Fill form and submit
4. Should work! ✅

---

## 🎯 Expected Outcome

After deployment:

```
✅ Backend deployed to: https://physio-monitoring-backend.onrender.com
✅ Health check working
✅ Registration endpoint ready
✅ Login endpoint ready
✅ Exercises API ready
✅ Frontend can reach backend
✅ CORS enabled
✅ Auto-restart enabled
✅ Logs accessible
```

---

## 📊 After Deployment

### Monitor
- Render dashboard shows service status
- View logs for any errors
- Monitor response times

### Optimize
- Start with Free tier
- Upgrade to Starter ($7/mo) for production
- Add PostgreSQL if needed

### Scale
- Free tier: ~100 concurrent users
- Starter: ~1000+ concurrent users

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Connection error" | Check `window.API_BASE_URL` in frontend |
| Build fails | Verify `requirements.txt` in `/physio-web/backend` |
| Database not working | Use SQLite (default) or add PostgreSQL |
| CORS blocked | Ensure CORS middleware enabled in app.py |
| Service won't restart | Check logs in Render dashboard |

---

## ✨ Success Indicators

You'll know it's working when:
- ✅ Backend health check returns 200 OK
- ✅ Registration creates new users
- ✅ Login returns JWT token
- ✅ Exercises API returns data
- ✅ Frontend can make API calls
- ✅ No CORS errors in browser console

---

## 📞 Need Help?

### Check Render Logs
1. Render Dashboard → Select Service
2. Click "Logs" tab
3. Look for errors

### Backend Status
- Running locally: `python app.py`
- No port conflicts
- All imports working

### Frontend Connection
- Browser Console (F12)
- Check `window.API_BASE_URL`
- Verify no CORS errors

---

## 🎉 Ready!

Your backend deployment is just **10 minutes away**! 

**Next**: Follow the Quick Deployment Steps above starting at 1️⃣

---

**Created**: March 26, 2026  
**Status**: Ready for Deployment  
**Estimated Time**: 10 minutes
