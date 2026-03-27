# Frontend Configuration Guide

## Setting Backend URL for Deployment

### 1. Local Development (Automatic)

No action needed. The app will auto-detect:
- Runs on `http://localhost:3000` (Vercel dev)
- Backend at `http://localhost:8000` (FastAPI)

### 2. Production Deployment (Vercel)

After deploying your backend, update your frontend configuration.

#### Method A: Hard-coded in HTML (Quick)

Edit `physio-web/frontend/index.html`:

Add this **right after `<head>` tag**, before any scripts load:

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PhysioMonitor - AI-Powered Physiotherapy</title>
    
    <!-- 🔧 CONFIGURE BACKEND API URL -->
    <script>
        // Production Backend URL - Change this to your deployed backend
        // Example: https://physio-monitoring-backend.onrender.com
        window.API_BASE_URL = 'https://physio-monitoring-backend.onrender.com';
        
        console.log('🔗 Backend API Base URL:', window.API_BASE_URL);
    </script>
    
    <!-- Rest of your head content -->
    <link rel="stylesheet" href="style.css?v=3">
    <!-- ... -->
</head>
```

#### Method B: Environment Variable (Recommended)

In Vercel Dashboard:

1. **Settings** → **Environment Variables**
2. Create variable:
   ```
   Name: API_BASE_URL
   Value: https://physio-monitoring-backend.onrender.com
   ```

Then update `index.html`:
```html
<script>
    // Try to get from environment, else use default
    window.API_BASE_URL = window.location.hostname === 'localhost' 
        ? 'http://localhost:8000' 
        : 'https://physio-monitoring-backend.onrender.com';
</script>
```

---

## Voice Assistant Settings

### Where Voice UI Appears

✅ **Shows on these pages**:
- Exercise category selection (`/exercises`)
- Exercise list (`/exerciseList`, `/allExercises`)
- Active exercise session (`/exercise`)
- Settings page (`/settings`)

✗ **Hidden on these pages**:
- Home
- Dashboard
- Reports
- Rehab Plan
- Chatbot

### Enable/Disable Voice

Users can:
1. Click the **microphone icon** (bottom right)
2. Toggle "Enable Voice Feedback"
3. Adjust speed and volume

---

## Auth Configuration

### Registration Flow

1. User fills form on frontend
2. Frontend sends `POST /register` to backend
3. Backend:
   - Checks if username/email exists
   - Hashes password
   - Stores in database
   - Returns user data

### Login Flow

1. User enters credentials
2. Frontend sends `POST /token` to backend
3. Backend:
   - Validates username/password
   - Creates JWT token
   - Returns `access_token`
4. Frontend stores token locally
5. Future requests include `Authorization: Bearer {token}`

### Common Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| "Connection error" | Backend URL wrong | Update `window.API_BASE_URL` |
| "Username already registered" (new user) | DB query issue | Check backend logs |
| CORS blocked | Headers missing | Verify CORS middleware enabled |
| Token expired | Token expired | Clear localStorage, re-login |

---

## Checking Configuration

### In Browser Console

```javascript
// Check API configuration
console.log('API_BASE_URL:', window.API_BASE_URL);
console.log('Current hostname:', window.location.hostname);

// Test API connection
fetch(window.API_BASE_URL + '/health')
    .then(r => r.json())
    .then(d => console.log('✅ Backend connected:', d))
    .catch(e => console.error('❌ Backend error:', e));
```

### Expected Response

```json
{
    "status": "healthy",
    "environment": "production",
    "version": "1.0.0",
    "timestamp": "2026-03-26T11:44:00.000000"
}
```

---

## Deployment Platforms

### Vercel (Frontend)

✅ Already configured  
URL: `https://your-app.vercel.app`

### Render (Backend)

1. Deploy backend
2. Get URL: `https://your-backend.onrender.com`
3. Update `window.API_BASE_URL` in frontend

### Railway (Backend)

1. Deploy backend
2. Get URL: `https://your-backend.railway.app`
3. Update `window.API_BASE_URL` in frontend

---

## Quick Test

1. Open DevTools (F12)
2. Console tab
3. Paste:
```javascript
fetch(window.API_BASE_URL + '/register', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        username: 'testuser',
        email: 'test@example.com',
        full_name: 'Test User',
        password: 'testpass123'
    })
})
.then(r => r.json())
.then(d => console.log('Response:', d))
.catch(e => console.error('Error:', e));
```

✅ If successful, user is created  
❌ If error, check backend logs

---

## Environment Variables Summary

| Variable | Value | Where | Required |
|----------|-------|-------|----------|
| `API_BASE_URL` | Backend URL | index.html or Vercel env | Yes (production) |
| `SECRET_KEY` | JWT secret | Backend `.env` | Yes |
| `DATABASE_URL` | DB connection | Backend `.env` | Yes |
| `CORS_ORIGINS` | Allowed domains | Backend config | Yes (production) |
| `ENVIRONMENT` | production/development | Backend `.env` | No |

---

## Frontend Script Load Order

Important: Scripts must load in this order:

1. ✅ `config.js` - Configuration
2. ✅ `script.js` - Main app + API_BASE definition
3. ✅ `voice-assistant-system.js` - Voice module
4. ✅ `voice-control.js` - Voice UI (uses API_BASE from script.js)

---

## Troubleshooting Commands

### Check if backend is reachable:
```bash
curl -X GET https://your-backend.onrender.com/health
```

### Test registration endpoint:
```bash
curl -X POST https://your-backend.onrender.com/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","full_name":"Test","password":"test123"}'
```

### View backend logs:
```bash
# Render dashboard → Logs
# Or SSH into backend and check:
tail -f /var/log/app.log
```

---

**Last Updated**: March 26, 2026  
**Version**: 1.0
