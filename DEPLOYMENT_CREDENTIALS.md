# 🔐 Deployment Credentials & URLs

**Status**: Ready to fill in after deployment

---

## 📋 Backend Deployment Info

### Generated Credentials
```
SECRET_KEY: [Generated from: python -c "import secrets; print(secrets.token_urlsafe(32))"]
```

### Render Service
```
Service Name:       physio-monitoring-backend
Repository:         Physio-Monitoring
Branch:            main (or your branch)
Root Directory:     physio-web/backend
Deploy Date:       [Fill in after deployment]
```

### Backend URL
```
Production URL:    https://physio-monitoring-backend.onrender.com
Health Check:      https://physio-monitoring-backend.onrender.com/health
Exercises API:     https://physio-monitoring-backend.onrender.com/exercises
Register:          POST https://physio-monitoring-backend.onrender.com/register
Login:             POST https://physio-monitoring-backend.onrender.com/token
```

### Environment Variables (Set on Render)
```
ENVIRONMENT       = production
SECRET_KEY        = [Your generated key above]
DATABASE_URL      = (Left blank for SQLite default)
CORS_ORIGINS      = *
```

---

## 🌐 Frontend Configuration

### Frontend URL
```
Deployed on:       Vercel
Frontend URL:      https://physio-monitoring-web.vercel.app
GitHub Repo:       physio-web/frontend
```

### Frontend Environment Variables
```
Add to Vercel (or edit index.html):

File: physio-web/frontend/index.html
Location: Inside <head> tag, before other scripts
Content:
    <script>
        window.API_BASE_URL = 'https://physio-monitoring-backend.onrender.com';
    </script>
```

---

## 🔗 API Endpoints Reference

### Health & Status
```
GET /health
→ Returns: {"status": "healthy", "environment": "production"}
```

### Authentication
```
POST /register
Body: {"username": "user", "email": "user@example.com", "password": "pass"}
→ Returns: {"message": "User created successfully"}

POST /token
Body: {"username": "user", "password": "pass"}
→ Returns: {"access_token": "jwt_token", "token_type": "bearer"}

GET /me (requires auth token)
→ Returns: current user info
```

### Exercises
```
GET /exercises
→ Returns: list of all exercises

GET /exercises/{exercise_id}
→ Returns: specific exercise data

POST /exercises
Body: exercise data
→ Returns: created exercise
```

### WebSocket (Real-time)
```
WS /ws/pose
→ Real-time pose detection
```

---

## 📊 Deployment Timeline

| Time | Event |
|------|-------|
| T+0 min | Click "Create Web Service" on Render |
| T+2 min | Build starts (installing dependencies) |
| T+3 min | App starts running |
| T+4 min | Backend online and healthy |
| T+5 min | You test `/health` endpoint |
| T+6 min | Update frontend with backend URL |
| T+7 min | Frontend redeploys (Vercel auto-detects) |
| T+10 min | End-to-end testing complete |

---

## ✅ Post-Deployment Checklist

### Immediate Verification
- [ ] Backend URL accessible
- [ ] Health check returns 200
- [ ] Render logs show no errors
- [ ] Can curl endpoints successfully

### Frontend Update
- [ ] Added `window.API_BASE_URL` to index.html
- [ ] Redeployed frontend
- [ ] Frontend loads without 404s
- [ ] No CORS errors in console

### User Registration Test
- [ ] Can register new user
- [ ] No "connection error" displayed
- [ ] Credentials stored properly
- [ ] Can login with new account
- [ ] Dashboard loads successfully

### Full Flow Test
- [ ] Login with test account
- [ ] Upload exercises
- [ ] Get recommendations
- [ ] No API errors
- [ ] Performance acceptable

---

## 🐛 Troubleshooting Quick Links

### Backend Not Responding
```
Check Render logs (Dashboard → Logs tab)
Most common: Missing SECRET_KEY env variable
Fix: Add SECRET_KEY to Render environment variables
```

### CORS Errors in Frontend
```
Error will show in browser console (F12 → Console)
Check: window.API_BASE_URL is correct
Fix: Ensure no typos in backend URL
```

### Database Not Initializing
```
SQLite auto-initializes on first run
No setup needed unless using PostgreSQL
Check Render logs for database errors
```

### Build Failing on Render
```
Check Render build logs
Most common: requirements.txt not found
Fix: Verify Root Directory is set to physio-web/backend
```

---

## 📱 Connection Status

### Local Development
```
Frontend:    http://localhost:3000 (if running locally)
Backend:     http://localhost:8000 (default)
Auto-detect: getAPIBaseURL() function handles this
```

### Production
```
Frontend:    https://physio-monitoring-web.vercel.app
Backend:     https://physio-monitoring-backend.onrender.com
Manual URL:  Set window.API_BASE_URL in index.html
```

---

## 🔄 API Communication Flow

```
[Vercel Frontend]
         ↓
 window.API_BASE_URL = "https://physio-monitoring-backend.onrender.com"
         ↓
[fetch() calls]
         ↓
[Render Backend on uvicorn]
         ↓
[SQLite Database]
```

---

## 📝 Notes

- Backend deployment: one-time setup (~5 min)
- Frontend update: simple add 5 lines (~1 min)
- Database: pre-configured SQLite, no migration needed
- Auto-restarts enabled on crashes
- Logs available in Render dashboard 24/7

---

## 🎯 Next Steps

1. ✅ _Checked pre-deployment readiness_
2. ⏳ _Ready to deploy backend_
3. ⏳ _Update frontend with backend URL_
4. ⏳ _End-to-end testing_

---

**Ready to proceed?** → Go to https://render.com and start deployment!

**Questions?** → Check DEPLOYMENT_READY.md for quick reference
