# Environment Variables Reference

This file documents all environment variables needed for production deployment.

## Backend Environment Variables

Set these in your Render/Railway deployment dashboard.

### Required Variables

| Variable | Value | Example | Notes |
|----------|-------|---------|-------|
| `ENVIRONMENT` | production | production | Toggles production mode |
| `SECRET_KEY` | Generated secure key | `Y8x9mK2pL5vJ3nQ1wR6tU9bD4fG7cH0aE2sL8pK5jH3xN` | Generate: `python -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `DATABASE_URL` | PostgreSQL connection | `postgresql://user:pass@host:5432/db` | **Keep secure!** |
| `CORS_ORIGINS` | Frontend domains | `https://app.vercel.app,https://example.com` | Comma-separated, no spaces |
| `PORT` | Server port | 8000 | Let platform override |

### Optional Variables

| Variable | Value | Default | Purpose |
|----------|-------|---------|---------|
| `LOG_LEVEL` | Logging level | info | Options: debug, info, warning, error |
| `ML_MODEL_PATH` | Models directory | ./ml_models | Path to ML model files |
| `ENABLE_ADVANCED_ML` | Boolean | true | Enable advanced ML models |
| `ENABLE_VOICE` | Boolean | true | Enable voice features |
| `TTS_SERVICE` | Service name | gtts | Options: pyttsx3, gtts |

### Generation Examples

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Build PostgreSQL connection string
# Format: postgresql://username:password@host:port/database
# Example: postgresql://physio_user:MySecurePass123!@dpg-abc123.render-sydney.internal:5432/physio_monitoring
```

---

## Frontend Environment Variables

Set these in your Vercel/Netlify deployment dashboard.

### Required Variables

| Variable | Value | Example | Notes |
|----------|-------|---------|-------|
| `REACT_APP_API_URL` | Backend API URL | `https://physio-backend.onrender.com` | Must be HTTPS in production |

### Optional Variables

| Variable | Value | Default | Purpose |
|----------|-------|---------|---------|
| `REACT_APP_ENVIRONMENT` | Environment | production | Toggles UI features |
| `REACT_APP_LOG_LEVEL` | Logging level | info | Console log verbosity |
| `REACT_APP_ENABLE_ANALYTICS` | Boolean | false | Enable analytics |

---

## Setting Variables by Platform

### Render Dashboard

1. Go to your Web Service
2. Click "Environment"
3. Click "Add Environment Variable"
4. Enter Key and Value
5. Click "Save"
6. Service redeploys automatically

### Railway Dashboard

1. Go to your service
2. Click "Variables"
3. Click "New Variable"
4. Enter Key and Value
5. Click "Save"
6. Service redeploys automatically

### Vercel Dashboard

1. Go to Project Settings
2. Click "Environment Variables"
3. Enter Variable Name and Value
4. Select environments: Production, Preview, Development
5. Click "Save"
6. Go to "Deployments" → Redeploy to apply changes

### Netlify Dashboard

1. Go to Site Settings
2. Click "Build & Deploy" → "Environment"
3. Click "New variable"
4. Enter Key and Value
5. Click "Save"
6. Trigger new deployment

---

## Security Best Practices

### 🔐 DO

✅ Store secrets in environment variables
✅ Use strong passwords (20+ characters)
✅ Rotate credentials regularly
✅ Use HTTPS/SSL everywhere
✅ Enable CORS only for needed domains
✅ Use separate credentials per environment (dev, staging, prod)
✅ Keep .env files out of version control

### ❌ DON'T

❌ Commit .env files to Git
❌ Hardcode secrets in code
❌ Use same credentials for dev and prod
❌ Share production secrets via email
❌ Allow wildcards in CORS origins (* is okay for dev only)
❌ Commit database backups to Git
❌ Use weak passwords

---

## Variable Examples

### Complete Backend Example

```
ENVIRONMENT=production
SECRET_KEY=Y8x9mK2pL5vJ3nQ1wR6tU9bD4fG7cH0aE2sL8pK5jH3xN
DATABASE_URL=postgresql://physio_user:MySecurePassword123@dpg-abc123.render-sydney.internal:5432/physio_monitoring_prod
CORS_ORIGINS=https://physio-app.vercel.app,https://www.physio-app.com,https://physio-app.netlify.app
PORT=8000
PYTHONUNBUFFERED=1
LOG_LEVEL=info
ML_MODEL_PATH=./ml_models
ENABLE_ADVANCED_ML=true
ENABLE_VOICE=true
TTS_SERVICE=gtts
```

### Complete Frontend Example

```
REACT_APP_API_URL=https://physio-backend.onrender.com
REACT_APP_ENVIRONMENT=production
REACT_APP_LOG_LEVEL=info
REACT_APP_ENABLE_ANALYTICS=true
```

---

## Variable Validation

Before deploying, verify:

- [ ] All required variables are set
- [ ] No typos in variable names
- [ ] SECRET_KEY is at least 32 characters
- [ ] DATABASE_URL is a valid PostgreSQL connection string
- [ ] CORS_ORIGINS includes your frontend domain (exact match)
- [ ] API_URL in frontend points to backend domain
- [ ] No variables contain spaces or quotes (unless needed)
- [ ] No secrets in frontend environment (not sent to browser)

---

## Troubleshooting

### Variable Not Taking Effect

1. Check variable name spelling exactly (case-sensitive)
2. Redeploy application after changing variables
3. Clear browser cache
4. Check service logs for variable loading

### Connection String Format Wrong

Use this format:
```
postgresql://username:password@host:port/database
```

NOT:
```
postgres://... (deprecated syntax)
host=localhost... (connection string parameter syntax)
```

### CORS Issues

Check exact frontend domain:
- With www: `https://www.example.com`
- Without www: `https://example.com`
- With subdomain: `https://app.example.com`

Both need separate entries in CORS_ORIGINS if needed.

---

## Reference

- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Python Secrets Module](https://docs.python.org/3/library/secrets.html)
- [Environment Best Practices](https://12factor.net/config)
