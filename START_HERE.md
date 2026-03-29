# Quick Setup - Neck Exercises Working

## Start Server (Port 8000)

### Option 1: Using PowerShell (Current)
```powershell
cd c:\Users\Murali\Desktop\Physio-Monitoring\physio-web\backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### Option 2: Kill Existing Process and Restart
```powershell
# Kill any existing process on port 8000
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue).OwningProcess -Force -ErrorAction SilentlyContinue

# Wait a moment
Start-Sleep -Seconds 2

# Start server
cd c:\Users\Murali\Desktop\Physio-Monitoring\physio-web\backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

## Access Website
Once server is running, open browser:
```
http://localhost:8000
```

## Test Neck Exercises
1. **Register or Login**
   - Create account or use existing credentials

2. **Select Exercise**
   - Category: **Neck**
   - Exercise: Choose one of:
     - Neck Flexion
     - Neck Extension  
     - Neck Rotation

3. **Start Exercise**
   - Click "Start Exercise"
   - Allow camera access when prompted

4. **Perform Neck Movements**
   - Move neck slowly (2-3 seconds per movement)
   - Watch rep counter increment
   - View angle in real-time
   - See quality score

5. **Complete Session**
   - Do 5+ reps
   - Exit exercise
   - Refresh dashboard to see weekly activity

## Expected Output

**In Browser Console (F12):**
```
Development mode - using local backend: http://localhost:8000
Connecting WebSocket to: ws://localhost:8000/ws/USER_ID
WebSocket connected
Frame sent: {type: "frame", exercise_name: "Neck Flexion", ...}
Received: {reps: 1, angle: 35.2, quality_score: 0.85, ...}
```

**In Browser UI:**
- Live video from webcam
- Rep counter (incrementing)
- Current angle (e.g., "Angle: 35.2°")
- Quality score (0-100)
- Exercise message (e.g., "Good form!")

## Verify Everything Works

### Test 1: Backend is running
```bash
curl http://localhost:8000/health
# Should return: {"status": "healthy", ...}
```

### Test 2: Pose detector working
```powershell
cd c:\Users\Murali\Desktop\Physio-Monitoring
python test_neck_detection.py
# Should show: [SUCCESS] Neck exercise detection is working!
```

### Test 3: Frontend loads
```
http://localhost:8000
# Should load the full website
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Port 8000 in use | Kill: `Stop-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess -Force` |
| Camera not working | Allow camera in browser settings, try different browser |
| No WebSocket connection | Check browser console (F12) for errors |
| No reps detected | Move neck more deliberately, improve lighting |
| Server crashes | Check task manager, kill any python processes, restart |

## Files Modified

✅ **Fixed File:**
- `physio-web/backend/exercise_engine/engine.py` (Line 281)
  - Changed condition from `if MEDIAPIPE_AVAILABLE and mp_pose:` to `if mp_pose and hasattr(mp_pose, 'Pose'):`
  - This allows OpenCV fallback pose detector to initialize

## What's Running

```
Backend: FastAPI (Python)
Port: 8000 (or 9000)
Frontend: HTML5 + JavaScript
Database: SQLite (physio_monitoring.db)
Pose Detection: OpenCV-based fallback
```

## Session Example

```
User Action                    Backend Processing
─────────────────────────────────────────────────────
1. Select "Neck Flexion"   →  Store exercise name
2. Start Exercise          →  Open WebSocket connection
3. WebSocket connects      →  Initialize pose detector
4. User moves neck         →  Send frame via WebSocket
5. Backend receives frame  →  Detect 33 landmarks
6. Calculate angle         →  Compare to baseline
7. Increment rep count    →  Send feedback to UI
8. UI updates             →  Display reps, angle, score
9. User completes         →  Save to database
10. Close session         →  Store weekly statistics
```

## Next Steps

1. ✅ Start the backend server
2. ✅ Open http://localhost:8000 in browser
3. ✅ Select a neck exercise
4. ✅ Test rep detection
5. ✅ Verify data saves to dashboard

**The system is ready - just start the server and test!**
